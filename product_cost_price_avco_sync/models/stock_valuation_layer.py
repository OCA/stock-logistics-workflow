# Copyright 2020-2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from collections import OrderedDict, defaultdict, deque

from odoo import api, exceptions, models
from odoo.tools import float_compare, float_is_zero, float_round, groupby

# Matches the price at the end of the description core writes when the cost is
# modified by hand, both for a product and for a lot. The label is translated,
# but the number is always the last thing in it.
MANUAL_ADJUSTMENT_PRICE = re.compile(r"([+-]?\d+(?:[.,]\d+)?)\s*\)\s*$")

# How many layers of a chain are read at once while replaying it
AVCO_SYNC_BATCH = 1000


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = "stock.valuation.layer"

    def _get_avco_sync_key(self):
        """Return the valuation chain this layer belongs to.

        Odoo keeps one average cost per product, or one per lot when the
        product is valuated by lot, and both kinds of product coexist in the
        same database. The key carries the lot only in the second case, so the
        layers a product already had before being switched to valuation by lot,
        which carry no lot, keep replaying as the single chain they were.
        """
        self.ensure_one()
        lot = self.lot_id if self.product_id.lot_valuated else self.env["stock.lot"]
        return (self.product_id, self.company_id, lot)

    def _filter_avco_sync_entry_points(self):
        """Reduce a selection of layers to the ones worth replaying from.

        Replaying a chain corrects every layer that comes after the starting
        point, so out of a selection only the oldest layer of each chain is
        needed: the rest would redo the very same work. With valuation by lot
        that is the oldest of each lot, since each lot is a chain of its own.
        """
        entry_points = {}
        for svl in self.sorted(lambda x: (x.create_date, x.id)):
            if (
                svl.stock_valuation_layer_id
                or svl.product_id.with_company(svl.company_id).cost_method != "average"
            ):
                continue
            entry_points.setdefault(svl._get_avco_sync_key(), svl)
        return self.browse([svl.id for svl in entry_points.values()])

    def action_force_avco_sync(self):
        """Replay the valuation chain of the selected layers.

        Meant for the times a correction could not run on its own, such as
        layers written while the module was not installed, or a product whose
        cost drifted for any other reason.
        """
        for svl in self._filter_avco_sync_entry_points():
            svl._cost_price_avco_sync()
        return True

    def _get_avco_chain_domain(self):
        """Domain selecting every layer of the same valuation chain as self."""
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("product_id", "=", self.product_id.id),
        ]
        if self.product_id.lot_valuated:
            domain.append(("lot_id", "=", self.lot_id.id))
        return domain

    def write(self, vals):
        """Update cost price avco"""
        sync = ("unit_cost" in vals or "quantity" in vals) and not self.env.context.get(
            "skip_avco_sync"
        )
        res = True
        if sync or "unit_cost" in vals:
            for svl in self:
                svl_vals = dict(vals)
                if sync:
                    # Adjust total and write sequentially
                    svl_vals["value"] = vals.get("quantity", svl.quantity) * vals.get(
                        "unit_cost", svl.unit_cost
                    )
                svl._add_avco_remaining_value_delta(svl_vals)
                res = super(StockValuationLayer, svl).write(svl_vals) and res
        else:
            res = super().write(vals)
        if sync and self:
            # Sync the lowest SVL of each valuation chain
            for _key, elems in groupby(
                self.sorted(lambda x: (x.create_date, x.id)),
                lambda x: x._get_avco_sync_key(),
            ):
                elems[0]._cost_price_avco_sync()
        return res

    def _get_next_svls_to_sync_avco(self, limit=None):
        """Layers of the same chain that come after this one, in order."""
        self.ensure_one()
        domain = self._get_avco_chain_domain() + [
            "|",
            "&",
            ("create_date", "=", self.create_date),
            ("id", ">", self.id),
            ("create_date", ">", self.create_date),
        ]
        return (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(domain, order="create_date, id", limit=limit)
        )

    def _get_next_svl_to_sync_avco(self):
        return self._get_next_svls_to_sync_avco(limit=1)

    def _pop_next_avco_svl(self, svl_dic):
        """Return the next layer of the chain, reading them in batches.

        A chain can be hundreds of thousands of layers long, and asking for the
        next one at a time means one query per layer.
        """
        pending = svl_dic.get("pending")
        if not pending:
            pending = deque(self._get_next_svls_to_sync_avco(limit=AVCO_SYNC_BATCH))
            svl_dic["pending"] = pending
        return pending.popleft() if pending else self.browse()

    def _is_avco_sync_processable(self, svls_dic):
        """Method to be overrided in extension modules for blocking the sync in
        specific cases (like manufactured or component products) where we don't still
        have the needed data.
        """
        self.ensure_one()
        return True

    @api.model
    def _update_avco_svl_values(self, svl_dic, unit_cost=None):
        """Helper method for updating chained fields in SVL easily."""
        if unit_cost is not None:
            svl_dic["unit_cost"] = unit_cost
        svl_dic["value"] = svl_dic["unit_cost"] * svl_dic["quantity"]

    @api.model
    def _get_avco_svl_price(self, previous_unit_cost, previous_qty, unit_cost, qty):
        """Helper method for computing AVCO price based on previous and current
        information,

        When there are no positive units left to average against, that is, when
        ~previous_qty~ is zero or negative because the product was oversold, the
        incoming cost becomes the new average. The outstanding deficit will be
        settled by future receipts and core's own negative stock vacuum
        (`product._run_fifo_vacuum`) re-prices it with exactly that incoming
        cost, so weighting against a quantity the company doesn't hold would
        only make both ends disagree.

        The result is never allowed to go negative: see
        `_get_avco_spread_unit_cost` for why an average cost below zero is not a
        valuation but a corruption.
        """
        precision_qty = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if float_compare(previous_qty, 0.0, precision_digits=precision_qty) <= 0:
            return unit_cost
        total_qty = previous_qty + qty
        price = (
            (previous_unit_cost * previous_qty + unit_cost * qty) / total_qty
            if total_qty
            else unit_cost
        )
        return price if price >= 0 else previous_unit_cost

    def _is_avco_spreadable_value(self):
        """Whether this value-only layer changes the cost of the stock on hand.

        A layer that only carries value hangs from another one, and the sign of
        that parent says who the value belongs to:

        - Parent is an INCOMING layer: landed costs and the vendor bill price
          difference. The value is part of what those units cost, so it belongs
          to whatever is left of them and must raise or lower the average.
        - Parent is an OUTGOING layer: core's negative stock revaluations
          (`Revaluation of ... (negative inventory)`, written by
          `product._run_fifo_vacuum`). They settle a deficit of units that have
          already left the company, so they say nothing about what the stock
          still on hand is worth. Spreading them over it is what produced costs
          of -5062 EUR/unit out of a -1120 EUR revaluation landing on 0.22
          units.
        """
        self.ensure_one()
        parent = self.stock_valuation_layer_id
        precision_qty = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return float_compare(parent.quantity, 0.0, precision_digits=precision_qty) > 0

    @api.model
    def _get_avco_spread_unit_cost(self, previous_unit_cost, previous_qty, value):
        """New running cost after spreading `value` over the units on hand.

        Dividing by `previous_qty` is only meaningful while that quantity can
        absorb the value: a revaluation of -1120 EUR landing when 0.22 units are
        held works out to -5093 EUR/unit.

        A negative average cost is not a low valuation, it is a corruption: it
        flips the sign of the value of every layer that comes after it, so
        outgoing moves start ADDING value and the product's totals cancel out to
        something plausible while every single layer inside is wrong. That is
        precisely what hides the damage from any report that reads the totals.

        So the spread is skipped when it would take the cost below zero. The
        value stays on its own layer and therefore in the product's total, which
        keeps the sum honest, but it stops being smeared over the rest of the
        history. What is left shows up as the gap between `value_svl` and
        `quantity_svl * standard_price`, which is a visible, fixable
        discrepancy, unlike a negative cost.
        """
        precision_qty = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if (
            not value
            or float_compare(previous_qty, 0.0, precision_digits=precision_qty) <= 0
        ):
            return previous_unit_cost
        spread = previous_unit_cost + value / previous_qty
        return spread if spread >= 0 else previous_unit_cost

    def _add_avco_outgoing_deficit(self, quantity):
        """Record that `quantity` units which had already left were never really
        received, so Odoo's negative stock vacuum settles them.

        A deficit lives as a negative `remaining_qty` on the outgoing layer that
        could not be covered, which is what the vacuum looks for. Reducing a
        receipt below what has already been delivered creates exactly that
        situation, with no outgoing move of its own to carry it, so it goes on
        the last one of the chain. Without this the deficit is invisible and the
        next receipt never re-prices it with what was really paid.
        """
        self.ensure_one()
        last_outgoing = (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(
                self._get_avco_chain_domain()
                + [("quantity", "<", 0), ("stock_move_id", "!=", False)],
                order="create_date desc, id desc",
                limit=1,
            )
        )
        if last_outgoing:
            last_outgoing.with_context(skip_avco_sync=True).remaining_qty -= quantity

    def _restate_avco_quantity(self, quantity_diff):
        """Add `quantity_diff` units to this layer, as if the move had always
        had the corrected quantity, and keep in step the remaining quantity
        Odoo uses for the negative stock vacuum and for the invoice price
        difference. See `stock.move.line._create_correction_svl` for why the
        layer is restated instead of corrected with a new one.
        """
        self.ensure_one()
        precision_qty = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        vals = {"quantity": self.quantity + quantity_diff}
        if float_compare(self.quantity, 0.0, precision_digits=precision_qty) > 0:
            # Units added to a receipt are on hand until an outgoing move takes
            # them. Taking away more than what is left means they had already
            # been delivered, so the chain is short by the difference.
            remaining = self.remaining_qty + quantity_diff
            if float_compare(remaining, 0.0, precision_digits=precision_qty) < 0:
                self._add_avco_outgoing_deficit(-remaining)
                remaining = 0.0
            vals["remaining_qty"] = remaining
            # As a delta, so that what a landed cost or an invoice price
            # difference added to the remaining value survives: that is not
            # purchase cost and does not follow the quantity received.
            vals["remaining_value"] = (
                self.remaining_value + (remaining - self.remaining_qty) * self.unit_cost
            )
        elif float_compare(quantity_diff, 0.0, precision_digits=precision_qty) < 0:
            # More units leaving: let Odoo take them from the layers that still
            # have stock, and keep whatever it couldn't cover as the deficit
            # the vacuum will settle with the next receipt.
            fifo_vals = self.product_id._run_fifo(
                abs(quantity_diff), self.company_id, lot=self.lot_id
            )
            vals["remaining_qty"] = self.remaining_qty + fifo_vals.get(
                "remaining_qty", 0.0
            )
        self.write(vals)

    def _get_manual_adjustment_price(self):
        """Return the cost a manual adjustment layer was created for, or None.

        Core only stores the difference in value, so the target price can be
        recovered from the description alone, which is the label it writes in
        `product._change_standard_price` and `stock.lot._change_standard_price`.
        """
        self.ensure_one()
        if not self._is_manual_adjustment():
            return None
        match = MANUAL_ADJUSTMENT_PRICE.search(self.description or "")
        return float(match.group(1).replace(",", ".")) if match else None

    @api.model
    def _process_avco_svl_manual_adjustements(self, svls_dic):
        accumulated_qty = accumulated_value = 0.0
        for svl, svl_dic in svls_dic.items():
            if not svl_dic["quantity"] and not svl_dic["unit_cost"]:
                standard_price = svl._get_manual_adjustment_price()
                if standard_price is not None:
                    svl_dic["value"] = (
                        standard_price * accumulated_qty
                    ) - accumulated_value
            accumulated_qty = accumulated_qty + svl_dic["quantity"]
            accumulated_value = accumulated_value + svl_dic["value"]

    def _get_flush_excluded_fields(self):
        """Helper method to get the fields that won't be rounded in the flush."""
        return []

    def _get_monetary_fields(self):
        """Helper method to get the fields to round to currency precision."""
        return ["unit_cost", "value"]

    @api.model
    def _flush_all_avco_sync(self, svls_dic, skip_avco_sync=True):
        """Check if there's something to write and write it in the DB."""
        for svl, svl_dic in svls_dic.items():
            vals = {}
            for field_name, new_value in svl_dic.items():
                if field_name == "id":
                    continue
                elif field_name in self._get_flush_excluded_fields():
                    vals[field_name] = new_value
                else:
                    # Currency decimal precision for values and high precision to others
                    if field_name in self._get_monetary_fields():
                        prec_digits = svl.currency_id.decimal_places
                    else:
                        prec_digits = 8
                    if svl[field_name] != 0.0 and float_is_zero(
                        new_value, precision_digits=prec_digits
                    ):
                        vals[field_name] = 0.0
                    elif float_compare(
                        svl[field_name], new_value, precision_digits=prec_digits
                    ):
                        vals[field_name] = new_value
            # Write modified fields
            if vals:
                svl.with_context(skip_avco_sync=skip_avco_sync).write(vals)

    def _add_avco_remaining_value_delta(self, vals):
        """Keep `remaining_value` in step with a cost the replay just changed.

        It is the value Odoo reads to know what the units still on hand are
        worth: the negative stock vacuum prices what it takes from a layer with
        `remaining_value / remaining_qty`, `stock_landed_costs` accumulates on
        it and the vendor bill price difference corrects over it. Leaving it
        behind would settle later deficits at the cost that was just proven
        wrong.

        The adjustment is a delta on purpose, so that whatever a landed cost or
        an invoice added to it survives: that is not purchase cost.
        """
        self.ensure_one()
        precision_qty = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if (
            "unit_cost" not in vals
            # Whoever passes it has already worked it out, as
            # `_restate_avco_quantity` does
            or "remaining_value" in vals
            or float_compare(self.quantity, 0.0, precision_digits=precision_qty) <= 0
            or float_is_zero(self.remaining_qty, precision_digits=precision_qty)
        ):
            return
        vals["remaining_value"] = self.remaining_value + self.remaining_qty * (
            vals["unit_cost"] - self.unit_cost
        )

    def _get_previous_svl_info(self):
        self.ensure_one()
        previous_svls = self.env["stock.valuation.layer"].search(
            self._get_avco_chain_domain()
            + [
                "|",
                "&",
                ("create_date", "=", self.create_date),
                ("id", "<", self.id),
                ("create_date", "<", self.create_date),
            ],
            order="create_date, id",
        )
        key = self._get_avco_sync_key()
        svls_dic = OrderedDict()
        svls_dic[key] = {
            "svls": OrderedDict(),
            "previous_unit_cost": 0,
            "previous_qty": 0,
            "unit_cost_processed": 0,
        }
        for svl in previous_svls:
            svl._process_avco_sync_one(svls_dic, dry=True)
        return (
            svls_dic[key]["previous_unit_cost"],
            svls_dic[key]["previous_qty"],
            svls_dic[key]["unit_cost_processed"],
        )

    def _initialize_avco_sync_struct(self):
        """Return the basic initialized structure for each valuation chain that
        is used for AVCO sync main loop.
        """
        self.ensure_one()
        prev_vals = self._get_previous_svl_info()
        return {
            "to_sync": self,
            "svls": OrderedDict(),
            "previous_unit_cost": prev_vals[0],
            "previous_qty": prev_vals[1],
            "unit_cost_processed": prev_vals[2],
        }

    def _initialize_avco_sync_svl_dic(self):
        """Return the basic initialized dictionary for each SVL in memory."""
        return {
            "id": self.id,
            "quantity": self.quantity,
            "unit_cost": self.unit_cost,
            "value": self.value,
        }

    def _is_avco_synced(self, svls_dic):
        """Helper method for indicating if the SVL represented by self is already synced
        in current synchronization structure, which is pass in ~svls_dic~.
        """
        self.ensure_one()
        to_sync = svls_dic[self._get_avco_sync_key()]["to_sync"]
        if not to_sync:
            return True
        return self.create_date < to_sync.create_date or (
            self.create_date == to_sync.create_date and self.id < to_sync.id
        )

    def _set_avco_chain_standard_price(self, key, unit_cost):
        """Write the cost the chain ended up with on whatever owns it: the lot
        for a product valuated by lot, the product otherwise.
        """
        product, company, lot = key
        precision_price = self.env["decimal.precision"].precision_get("Product Price")
        target = (lot or product).with_company(company)
        if float_compare(
            unit_cost, target.standard_price, precision_digits=precision_price
        ):
            target.with_context(
                disable_auto_svl=True
            ).sudo().standard_price = float_round(
                unit_cost, precision_digits=precision_price
            )

    def _cost_price_avco_sync(self):
        """Replay the valuation chain this layer belongs to, from here on."""
        self.ensure_one()
        precision_price = self.env["decimal.precision"].precision_get("Product Price")
        # Prepare structure for the main loop
        if self.product_id.cost_method != "average" or self.stock_valuation_layer_id:
            return
        svls_dic = OrderedDict()
        svls_dic[self._get_avco_sync_key()] = self._initialize_avco_sync_struct()
        # Main loop: iterate while there's something to do
        index = 0  # which valuation chain to process
        reloop = False  # activated when something is blocking
        any_processed = False  # to control if there's no progress in a whole loop
        while index < len(svls_dic):
            key = list(svls_dic.keys())[index]
            svl_dic = svls_dic[key]
            while svl_dic["to_sync"]:
                svl = svl_dic["to_sync"]
                if not svl._is_avco_sync_processable(svls_dic):
                    reloop = True
                    break
                svl._process_avco_sync_one(svls_dic)
                svl_dic["to_sync"] = svl._pop_next_avco_svl(svl_dic)
                any_processed = True
            index += 1
            if index >= len(svls_dic) and reloop:
                if not any_processed:
                    raise exceptions.UserError(
                        self.env._(
                            "The AVCO sync can't be completed, as there's some endless "
                            "dependency in the data needed to process it."
                        )
                    )
                any_processed = False
                index = 0
                reloop = False
        lot_valuated = defaultdict(lambda: self.env["product.product"])
        for key, svl_dic in svls_dic.items():
            # Reprocess svls to set manual adjust values take into account all vacuums
            self._process_avco_svl_manual_adjustements(svl_dic["svls"])
            # Write changes in db before deriving anything out of them
            self._flush_all_avco_sync(svl_dic["svls"])
            self._set_avco_chain_standard_price(key, svl_dic["previous_unit_cost"])
            product, company, lot = key
            if lot:
                lot_valuated[company] |= product
        # The cost of a product valuated by lot isn't replayed, it summarises
        # the lots that are in stock, so core derives it from the layers and so
        # do we.
        for company, products in lot_valuated.items():
            products._set_avco_standard_price_from_layers(company)
        # Update unit_cost for incoming stock moves
        if (
            self.stock_move_id
            and self.stock_move_id._is_in()
            and float_compare(
                self.stock_move_id.price_unit,
                self.unit_cost,
                precision_digits=precision_price,
            )
        ):
            self.stock_move_id.price_unit = self.unit_cost

    def _is_manual_adjustment(self):
        self.ensure_one()
        return (
            not self.unit_cost
            and not self.quantity
            and not self.stock_move_id
            and self.description
        )

    def _is_avco_valued_at_current_cost(self):
        """Layers whose unit cost is not a purchase price but whatever the
        product was worth when they were created, so replaying the chain has to
        re-price them instead of averaging them in: returns, inventory
        adjustments, and the layers core writes with no move at all to switch a
        product from one valuation model to another.
        """
        self.ensure_one()
        move = self.stock_move_id
        return not move or bool(move.move_orig_ids) or move.is_inventory

    def _process_avco_sync_one(self, svls_dic, dry=False):
        """Process the syncronization of the current SVL in self. If this method is
        executed, the sync is processable. If you need to block this processing,
        override `_is_avco_sync_processable` and return a falsy value there.

        Two things can be performed here:

        1. Modify current SVL dic for putting another values (quantity, unit_cost, etc).
           You have to update also internal structures, updating "previous_unit_cost"
           through `_update_avco_svl_values`, "unit_cost_processed", and using
           `_get_avco_svl_price`. Example:

            ```
            svl_dic = svls_dic[self._get_avco_sync_key()]
            svl_dic["svls"][self] = self._initialize_avco_sync_svl_dic()
            unit_cost = <new svl unit cost>
            svl_dic["unit_cost_processed"] = True
            svl_dic["previous_unit_cost"] = self._get_avco_svl_price(
                svl_dic["previous_unit_cost"],
                svl_dic["previous_qty"],
                unit_cost,
                self.quantity,
            )
            self._update_avco_svl_values(svl_dic["svls"][self], unit_cost=unit_cost)
            ```
        2. Add in the sync structure extra chains to sync. Example:

            ```
            svl = <svl_to_sync>
            key = svl._get_avco_sync_key()
            if key not in svls_dic:
                svls_dic[key] = svl._initialize_avco_sync_struct()
            ```

        If the argument ~~dry~~ is set to True, no sync enqueue should be done.
        """
        self.ensure_one()
        precision_qty = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        svl_dic = svls_dic[self._get_avco_sync_key()]
        svl_data = self._initialize_avco_sync_svl_dic()
        if not dry:
            # A dry run only wants the running cost and quantity it ends up
            # with. Keeping a dict per layer of a chain that can be hundreds of
            # thousands long, only to throw it away, is what makes replaying an
            # old correction expensive in memory.
            svl_dic["svls"][self] = svl_data
        # Layers that only carry value: landed costs, the invoice price
        # difference and core's own negative stock revaluations. Only the ones
        # that belong to the stock on hand change its cost, and only while that
        # stock can absorb them.
        if self.stock_valuation_layer_id:
            if self._is_avco_spreadable_value():
                svl_dic["previous_unit_cost"] = self._get_avco_spread_unit_cost(
                    svl_dic["previous_unit_cost"],
                    svl_dic["previous_qty"],
                    self.value,
                )
            return
        f_compare = float_compare(self.quantity, 0.0, precision_digits=precision_qty)
        # Keep the unit_cost if there's no previous incoming or manual adjustment
        if not svl_dic["unit_cost_processed"]:
            svl_dic["previous_unit_cost"] = self.unit_cost
            if f_compare > 0.0:
                svl_dic["unit_cost_processed"] = True
        # Incoming line in layer
        if f_compare > 0:
            if self._is_avco_valued_at_current_cost():
                self._update_avco_svl_values(
                    svl_data, unit_cost=svl_dic["previous_unit_cost"]
                )
            # Normal incoming moves
            else:
                svl_dic["unit_cost_processed"] = True
                svl_dic["previous_unit_cost"] = self._get_avco_svl_price(
                    svl_dic["previous_unit_cost"],
                    svl_dic["previous_qty"],
                    svl_data["unit_cost"],
                    self.quantity,
                )
            svl_dic["previous_qty"] += self.quantity
        # Outgoing line in layer
        elif f_compare < 0:
            self._update_avco_svl_values(
                svl_data, unit_cost=svl_dic["previous_unit_cost"]
            )
            svl_dic["previous_qty"] += self.quantity
        # Manual standard_price adjustment line in layer
        elif self._is_manual_adjustment():
            standard_price = self._get_manual_adjustment_price()
            if standard_price is not None:
                svl_dic["unit_cost_processed"] = True
                new_diff = standard_price - svl_dic["previous_unit_cost"]
                svl_data["value"] = new_diff * svl_dic["previous_qty"]
                svl_dic["previous_unit_cost"] = standard_price
            else:
                # The stock revaluation wizard names no target cost, it just
                # adds value to what is on hand: core picks the layers with
                # `remaining_qty` and splits the amount among them. So its value
                # belongs to the stock on hand and raises its cost, exactly like
                # a landed cost, only without a parent layer to hang from.
                svl_dic["previous_unit_cost"] = self._get_avco_spread_unit_cost(
                    svl_dic["previous_unit_cost"],
                    svl_dic["previous_qty"],
                    self.value,
                )
        # Incoming or Outgoing moves without quantity and unit_cost
        elif not self.quantity and self.stock_move_id:
            svl_data["value"] = 0.0

# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from collections import OrderedDict, defaultdict

from odoo import _, api, exceptions, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero, float_round, groupby


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = "stock.valuation.layer"

    def write(self, vals):
        """Update cost price avco"""
        svl_previous_vals = defaultdict(dict)
        if ("unit_cost" in vals or "quantity" in vals) and not self.env.context.get(
            "skip_avco_sync"
        ):
            for svl in self:
                svl_vals = vals.copy()
                for field_name in set(vals.keys()) & {"unit_cost", "quantity"}:
                    svl_previous_vals[svl][field_name] = svl[field_name]
                # Adjust total and write sequentially
                svl_vals["value"] = vals.get("quantity", svl.quantity) * vals.get(
                    "unit_cost", svl.unit_cost
                )
                res = super(StockValuationLayer, svl).write(svl_vals)
        else:
            res = super().write(vals)
        if svl_previous_vals:
            # Group by product and company, and sync the lowest SVL of each group
            self = self.sorted(lambda x: (x.create_date, x.id))
            for _group, elems in groupby(self, lambda x: (x.product_id, x.company_id)):
                elems[0]._cost_price_avco_sync(svl_previous_vals[elems[0]])
        return res

    def _get_next_svl_to_sync_avco(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("product_id", "=", self.product_id.id),
            "|",
            "&",
            ("create_date", "=", self.create_date),
            ("id", ">", self.id),
            ("create_date", ">", self.create_date),
        ]
        return (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(domain, order="create_date, id", limit=1)
        )

    def _is_avco_sync_processable(self, svls_dic):
        """Method to be overrided in extension modules for blocking the sync in
        specific cases (like manufactured or component products) where we don't still
        have the needed data.
        """
        self.ensure_one()
        return True

    @api.model
    def _process_avco_svl_inventory(self, svl_dic, qty_diff, previous_unit_cost):
        self.ensure_one()
        high_decimal_precision = 8
        new_svl_qty = svl_dic["quantity"] + qty_diff
        move = self.stock_move_id
        # Check if with the new difference the sign of the move changes
        if (new_svl_qty < 0 and move.location_id.usage == "inventory") or (
            new_svl_qty > 0 and move.location_dest_id.usage == "inventory"
        ):
            location_aux = move.location_id
            move.location_id = move.location_dest_id
            move.location_dest_id = location_aux
            move.move_line_ids.location_id = move.location_id
            move.move_line_ids.location_dest_id = move.location_dest_id
        # TODO: Split new_svl_qty in related stock move lines
        if (
            float_compare(
                abs(new_svl_qty),
                move.quantity_done,
                precision_digits=high_decimal_precision,
            )
            != 0
        ):
            if len(move.move_line_ids) > 1:
                raise ValidationError(
                    _(
                        "More than one stock move line to assign the new "
                        "stock valuation layer quantity"
                    )
                )
            move.quantity_done = abs(new_svl_qty)
        # Reasign qty variables
        qty = new_svl_qty
        svl_dic["quantity"] = new_svl_qty
        svl_dic["unit_cost"] = previous_unit_cost
        svl_dic["value"] = svl_dic["quantity"] * previous_unit_cost
        return qty

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
        """
        total_qty = previous_qty + qty
        return (
            (previous_unit_cost * previous_qty + unit_cost * qty) / total_qty
            if total_qty
            else unit_cost
        )

    @api.model
    def _process_avco_svl_manual_adjustements(self, svls_dic):
        accumulated_qty = accumulated_value = 0.0
        for svl, svl_dic in svls_dic.items():
            if (
                not svl_dic["quantity"]
                and not svl_dic["unit_cost"]
                and not svl.stock_move_id
                and svl.description
            ):
                match_price = re.findall(r"[+-]?[0-9]+\.[0-9]+\)$", svl.description)
                if match_price:
                    standard_price = float(match_price[0][:-1])
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

    def _get_previous_svl_info(self):
        self.ensure_one()
        previous_svls = self.env["stock.valuation.layer"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("company_id", "=", self.company_id.id),
                "|",
                "&",
                ("create_date", "=", self.create_date),
                ("id", "<", self.id),
                ("create_date", "<", self.create_date),
            ],
            order="create_date, id",
        )
        key = (self.product_id, self.company_id)
        svls_dic = OrderedDict()
        svls_dic[key] = {
            "svls": OrderedDict(),
            "previous_unit_cost": 0,
            "previous_qty": 0,
            "inventory_processed": 0,
            "unit_cost_processed": 0,
            "qty_diff": 0,
        }
        for svl in previous_svls:
            svl._process_avco_sync_one(svls_dic, dry=True)
        return (
            svls_dic[key]["previous_unit_cost"],
            svls_dic[key]["previous_qty"],
            svls_dic[key]["inventory_processed"],
            svls_dic[key]["unit_cost_processed"],
        )

    def _initialize_avco_sync_struct(self, svl_prev_vals):
        """Return the basic initialized structure for each pair (product, company)
        that is used for AVCO sync main loop.
        """
        self.ensure_one()
        prev_vals = self._get_previous_svl_info()
        return {
            "to_sync": self,
            "svls": OrderedDict(),
            "previous_unit_cost": prev_vals[0],
            "previous_qty": prev_vals[1],
            "inventory_processed": prev_vals[2],
            "unit_cost_processed": prev_vals[3],
            "qty_diff": self.quantity - svl_prev_vals.get("quantity", self.quantity),
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
        key = (self.product_id, self.company_id)
        to_sync = svls_dic[key]["to_sync"]
        if not to_sync:
            return True
        return self.create_date < to_sync.create_date or (
            self.create_date == to_sync.create_date and self.id < to_sync.id
        )

    def _cost_price_avco_sync(self, svl_prev_vals):
        self.ensure_one()
        dp_obj = self.env["decimal.precision"]
        precision_price = dp_obj.precision_get("Product Price")
        # Prepare structure for the main loop
        if self.product_id.cost_method != "average" or self.stock_valuation_layer_id:
            return
        svls_dic = OrderedDict()
        svls_dic[
            (self.product_id, self.company_id)
        ] = self._initialize_avco_sync_struct(svl_prev_vals)
        # Main loop: iterate while there's something to do
        index = 0  # which (product, company) to process
        reloop = False  # activated when something is blocking
        any_processed = False  # to control if there's no progress in a whole loop
        while index < len(svls_dic):
            product, company = list(svls_dic.keys())[index]
            svl_dic = svls_dic[(product, company)]
            while svl_dic["to_sync"]:
                svl = svl_dic["to_sync"]
                if not svl._is_avco_sync_processable(svls_dic):
                    reloop = True
                    break
                svl._process_avco_sync_one(svls_dic)
                svl_dic["to_sync"] = svl._get_next_svl_to_sync_avco()
                any_processed = True
            index += 1
            if index >= len(svls_dic) and reloop:
                if not any_processed:
                    raise exceptions.UserError(
                        _(
                            "The AVCO sync can't be completed, as there's some endless "
                            "dependency in the data needed to process it."
                        )
                    )
                any_processed = False
                index = 0
                reloop = False
        for product, company in svls_dic:
            svl_dic = svls_dic[(product, company)]
            # Reprocess svls to set manual adjust values take into account all vacuums
            self._process_avco_svl_manual_adjustements(svl_dic["svls"])
            # Update product standard price if it is modified
            if float_compare(
                svl_dic["previous_unit_cost"],
                product.with_company(company).standard_price,
                precision_digits=precision_price,
            ):
                product.with_company(company).with_context(
                    disable_auto_svl=True
                ).sudo().standard_price = float_round(
                    svl_dic["previous_unit_cost"], precision_digits=precision_price
                )
            # Write changes in db
            self._flush_all_avco_sync(svl_dic["svls"])
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

    def _process_avco_sync_one(self, svls_dic, dry=False):  # noqa: C901
        """Process the syncronization of the current SVL in self. If this method is
        executed, the sync is processable. If you need to block this processing,
        override `_is_avco_sync_processable` and return a falsy value there.

        Two things can be performed here:

        1. Modify current SVL dic for putting another values (quantity, unit_cost, etc).
           You have to update also internal structures, updating "previous_unit_cost"
           through `_update_avco_svl_values`, "unit_cost_processed", and using
           `_get_avco_svl_price`. Example:

            ```
            svl_dic = svls_dic[(self.product_id, self.company_id)]
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
        2. Add in the sync structure extra products to sync. Example:

            ```
            svl = <svl_to_sync>
            key = (svl.product_id, svl.company_id)
            if key not in svls_dic:
                svls_dic[key] = svl._initialize_avco_sync_struct({})
            ```

        If the argument ~~dry~~ is set to True, no sync enqueue should be done.
        """
        self.ensure_one()
        dp_obj = self.env["decimal.precision"]
        precision_qty = dp_obj.precision_get("Product Unit of Measure")
        svl_dic = svls_dic[(self.product_id, self.company_id)]
        svl_dic["svls"][self] = self._initialize_avco_sync_svl_dic()
        svl_data = svl_dic["svls"][self]
        # Compatibility with landed cost
        if self.stock_valuation_layer_id:
            if self.value and svl_dic["previous_qty"]:
                svl_dic["previous_unit_cost"] += self.value / svl_dic["previous_qty"]
            return
        f_compare = float_compare(self.quantity, 0.0, precision_digits=precision_qty)
        # Keep inventory unit_cost if not previous incoming or manual adjustment
        if not svl_dic["unit_cost_processed"]:
            svl_dic["previous_unit_cost"] = self.unit_cost
            if f_compare > 0.0:
                svl_dic["unit_cost_processed"] = True
        # Adjust inventory IN and OUT
        if (
            (
                self.stock_move_id.location_id.usage == "inventory"
                or self.stock_move_id.location_dest_id.usage == "inventory"
            )
            # Discard moves with a picking because they are not an inventory
            and not self.stock_move_id.picking_id
            and not self.stock_move_id.scrapped
        ):
            if (
                not svl_dic["inventory_processed"]
                # Context to keep stock quantities after inventory qty update
                and self.env.context.get("keep_avco_inventory", False)
            ):
                qty = self._process_avco_svl_inventory(
                    svl_data,
                    svl_dic["qty_diff"],
                    svl_dic["previous_unit_cost"],
                )
                svl_dic["inventory_processed"] = True
            else:
                qty = svl_data["quantity"]
                self._update_avco_svl_values(
                    svl_data, unit_cost=svl_dic["previous_unit_cost"]
                )
            svl_dic["previous_qty"] += qty
        # Incoming line in layer
        elif f_compare > 0:
            # Return moves
            if not self.stock_move_id or self.stock_move_id.move_orig_ids:
                self._update_avco_svl_values(
                    svl_data, unit_cost=svl_dic["previous_unit_cost"]
                )
            # Normal incoming moves
            else:
                svl_dic["unit_cost_processed"] = True
                if svl_dic["previous_qty"] <= 0.0:
                    # Set income svl.unit_cost as previous_unit_cost
                    svl_dic["previous_unit_cost"] = svl_data["unit_cost"]
                else:
                    svl_dic["previous_unit_cost"] = self._get_avco_svl_price(
                        svl_dic["previous_unit_cost"],
                        svl_dic["previous_qty"],
                        self.unit_cost,
                        self.quantity,
                    )
            svl_dic["previous_qty"] += self.quantity
        # Outgoing line in layer
        elif f_compare < 0:
            # Normal OUT
            self._update_avco_svl_values(
                svl_data, unit_cost=svl_dic["previous_unit_cost"]
            )
            svl_dic["previous_qty"] += self.quantity
        # Manual standard_price adjustment line in layer
        elif self._is_manual_adjustment():
            match_price = re.findall(r"[+-]?[0-9]+\.[0-9]+\)$", self.description)
            if match_price:
                svl_dic["unit_cost_processed"] = True
                standard_price = float(match_price[0][:-1])
                # TODO: Review abs in previous_qty or new_diff
                new_diff = standard_price - svl_dic["previous_unit_cost"]
                svl_data["value"] = new_diff * svl_dic["previous_qty"]
                svl_dic["previous_unit_cost"] = standard_price
        # Incoming or Outgoing moves without quantity and unit_cost
        elif not self.quantity and self.stock_move_id:
            svl_data["value"] = 0.0

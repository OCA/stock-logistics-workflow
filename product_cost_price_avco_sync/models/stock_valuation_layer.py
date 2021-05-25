# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_vacuum(self, company=None):
        if self.cost_method != "average":
            return super()._run_fifo_vacuum()


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = "stock.valuation.layer"

    @api.model
    def create(self, vals):
        svl = super().create(vals)
        if vals.get("quantity", 0.0) > 0.0 and svl.product_id.cost_method == "average":
            svl_remaining = self.sudo().search(
                [
                    ("company_id", "=", svl.company_id.id),
                    ("product_id", "=", svl.product_id.id),
                    ("remaining_qty", "<", 0.0),
                ],
                order="id",
                limit=1,
            )
            if svl_remaining:
                svl.cost_price_avco_sync({})
        return svl

    def write(self, vals):
        """ Update cost price avco """
        if ("unit_cost" in vals or "quantity" in vals) and not self.env.context.get(
            "skip_avco_sync"
        ):
            self.cost_price_avco_sync(vals)
        return super().write(vals)

    def get_svls_to_avco_sync(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("product_id", "=", self.product_id.id),
        ]
        return (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(domain, order="create_date, id")
        )

    @api.model
    def get_avco_svl_qty_unit_cost(self, line, svl, vals):
        if svl.id == line.id:
            qty = vals.get("quantity", line.quantity)
            unit_cost = vals.get("unit_cost", line.unit_cost)
        else:
            qty = svl.quantity
            unit_cost = svl.unit_cost
        return qty, unit_cost

    @api.model
    def process_avco_svl_inventory(self, svl, line, vals, previous_unit_cost):
        precision_qty = line.uom_id.rounding
        new_svl_qty = float_round(
            svl.quantity + (line.quantity - vals["quantity"]),
            precision_rounding=precision_qty,
        )
        # Check if with the new difference the sign of the move changes
        if (new_svl_qty < 0 and svl.stock_move_id.location_id.usage == "inventory") or (
            new_svl_qty > 0 and svl.stock_move_id.location_dest_id.usage == "inventory"
        ):
            location_aux = svl.stock_move_id.location_id
            svl.stock_move_id.location_id = svl.stock_move_id.location_dest_id
            svl.stock_move_id.location_dest_id = location_aux
            svl.stock_move_id.move_line_ids.location_id = svl.stock_move_id.location_id
            svl.stock_move_id.move_line_ids.location_dest_id = (
                svl.stock_move_id.location_dest_id
            )
        # TODO: Split new_svl_qty in related stock move lines
        if (
            float_compare(
                abs(new_svl_qty),
                svl.stock_move_id.quantity_done,
                precision_rounding=precision_qty,
            )
            != 0
        ):
            if len(svl.stock_move_id.move_line_ids) > 1:
                raise ValidationError(
                    _(
                        "More than one stock move line to assign the new "
                        "stock valuation layer quantity"
                    )
                )
            svl.stock_move_id.quantity_done = abs(new_svl_qty)
        # Reasign qty variables
        qty = new_svl_qty
        svl.quantity = new_svl_qty
        svl.unit_cost = line.currency_id.round(previous_unit_cost)
        svl.value = line.currency_id.round(svl.quantity * previous_unit_cost)
        # if update_enabled and "quantity" in vals:
        if new_svl_qty > 0:
            svl.remaining_qty = new_svl_qty
        else:
            svl.remaining_qty = 0.0
        svl.remaining_value = line.currency_id.round(svl.unit_cost * svl.remaining_qty)
        return qty

    def update_avco_svl_values(self, unit_cost=None, remaining_qty=None):
        for svl in self:
            if unit_cost is not None:
                svl.unit_cost = svl.currency_id.round(unit_cost)
            svl.value = svl.currency_id.round(svl.unit_cost * svl.quantity)
            if remaining_qty is not None:
                svl.remaining_qty = remaining_qty
            svl.remaining_value = svl.currency_id.round(
                svl.unit_cost * svl.remaining_qty
            )

    def get_avco_svl_price(
        self, previous_unit_cost, previous_qty, unit_cost, qty, total_qty
    ):
        self.ensure_one()
        return self.currency_id.round(
            ((previous_unit_cost * previous_qty + unit_cost * qty) / total_qty)
            if total_qty
            else unit_cost
        )

    def vacumm_avco_svl(self, qty, svls_to_avco_sync, vacuum_dic):
        self.ensure_one()
        precision_qty = self.uom_id.rounding
        vacuum_qty = qty
        for svl_to_vacuum in svls_to_avco_sync.filtered(
            lambda ln: ln.remaining_qty < 0 and ln.quantity < 0.0
        ):
            if not svl_to_vacuum.quantity:
                continue
            if abs(svl_to_vacuum.remaining_qty) <= vacuum_qty:
                vacuum_qty = float_round(
                    vacuum_qty + svl_to_vacuum.remaining_qty,
                    precision_rounding=precision_qty,
                )
                diff_qty = -svl_to_vacuum.remaining_qty
                new_remaining_qty = 0.0
            else:
                new_remaining_qty = float_round(
                    svl_to_vacuum.remaining_qty + vacuum_qty,
                    precision_rounding=precision_qty,
                )
                diff_qty = vacuum_qty
                vacuum_qty = 0.0
            vacuum_dic[svl_to_vacuum.id].append((diff_qty, self.unit_cost))
            # if svl.id != line.id:
            x = 0.0
            for q, c in vacuum_dic[svl_to_vacuum.id]:
                x += q * c
            if new_remaining_qty:
                x += abs(new_remaining_qty) * vacuum_dic[svl_to_vacuum.id][0][1]
            new_unit_cost = x / abs(svl_to_vacuum.quantity)

            new_value = svl_to_vacuum.quantity * new_unit_cost
            svl_to_vacuum.remaining_qty = new_remaining_qty
            svl_to_vacuum.remaining_value = new_remaining_qty * new_unit_cost
            svl_to_vacuum.unit_cost = new_unit_cost
            svl_to_vacuum.value = new_value
            # Update remaining in incoming line
            self.remaining_qty = vacuum_qty
            self.remaining_value = vacuum_qty * self.unit_cost
            if vacuum_qty == 0.0:
                break

    def update_remaining_avco_svl_in(self, svls_to_avco_sync):
        for svl in self:
            precision_qty = svl.uom_id.rounding
            svl_out_qty = svl.quantity
            for svl_in_remaining in svls_to_avco_sync.filtered(
                lambda ln: ln.remaining_qty > 0
            ):
                if abs(svl_out_qty) <= svl_in_remaining.remaining_qty:
                    new_remaining_qty = svl_in_remaining.remaining_qty + svl_out_qty
                    svl_out_qty = 0.0
                else:
                    svl_out_qty = float_round(
                        svl_out_qty + svl_in_remaining.remaining_qty,
                        precision_rounding=precision_qty,
                    )
                    new_remaining_qty = 0.0
                svl_in_remaining.update_avco_svl_values(remaining_qty=new_remaining_qty)
                if svl_out_qty == 0.0:
                    break

    def process_avco_svl_manual_adjustements(self, svls_to_avco_sync, vals):
        for line in self:
            precision_qty = line.uom_id.rounding
            accumulated_qty = accumulated_value = 0.0
            for svl in svls_to_avco_sync:
                if not svl.quantity and not svl.unit_cost and not svl.stock_move_id:
                    standard_price = float(svl.description.split(" ")[-1][:-1])
                    adjust_value = (
                        standard_price * accumulated_qty
                    ) - accumulated_value
                    if svl.value != adjust_value:
                        svl.value = adjust_value
                if svl.id == line.id:
                    accumulated_qty = float_round(
                        accumulated_qty + vals.get("quantity", line.quantity),
                        precision_rounding=precision_qty,
                    )
                    accumulated_value = line.currency_id.round(
                        accumulated_value
                        + vals.get("unit_cost", line.unit_cost)
                        * vals.get("quantity", line.quantity)
                    )
                else:
                    accumulated_qty = float_round(
                        accumulated_qty + svl.quantity, precision_rounding=precision_qty
                    )
                    accumulated_value = line.currency_id.round(
                        accumulated_value + svl.value
                    )

    def cost_price_avco_sync(self, vals):  # noqa: C901
        procesed_lines = set()
        # precision_price = self.env["decimal.precision"].precision_get("Product Price")
        for line in self.sorted(key=lambda l: (l.create_date, l.id)):
            if (
                line.id in procesed_lines
                or line.product_id.cost_method != "average"
                # or line.quantity < 0.0
            ):
                continue
            previous_unit_cost = previous_qty = 0.0
            # update_enabled determines if svl is after modified line to enable
            # write changes
            update_enabled = False
            svls_to_avco_sync = line.with_context(
                skip_avco_sync=True
            ).get_svls_to_avco_sync()
            precision_qty = (
                line.uom_id.rounding
            )  # self.env["decimal.precision"].precision_get("Product Unit of Measure")
            # precision_price = line.currency_id.rounding
            vacuum_dic = defaultdict(list)
            inventory_processed = False
            unit_cost_processed = False
            for svl in svls_to_avco_sync:
                qty, unit_cost = self.get_avco_svl_qty_unit_cost(line, svl, vals)
                # Keep inventory unit_cost if not previous incoming or manual adjustment
                if not unit_cost_processed:
                    previous_unit_cost = unit_cost
                f_compare = float_compare(qty, 0.0, precision_rounding=precision_qty)
                # Adjust inventory IN and OUT
                # Discard moves with a picking because they are not an inventory
                if (
                    (
                        svl.stock_move_id.location_id.usage == "inventory"
                        or svl.stock_move_id.location_dest_id.usage == "inventory"
                    )
                    and not svl.stock_move_id.picking_id
                    and not svl.stock_move_id.scrapped
                ):
                    if (
                        update_enabled
                        and "quantity" in vals
                        and not inventory_processed
                        # Context to keep stock quantities after inventory qty update
                        and self.env.context.get("keep_avco_inventory", False)
                    ):
                        qty = self.process_avco_svl_inventory(
                            svl, line, vals, previous_unit_cost
                        )
                        inventory_processed = True
                    else:
                        # TODO: Is necessary?
                        svl.update_avco_svl_values(unit_cost=previous_unit_cost)
                    # Check if adjust IN and we have moves to vacuum outs without stock
                    if (
                        update_enabled
                        and "quantity" in vals
                        and svl.quantity > 0.0
                        and previous_qty < 0.0
                    ):
                        svl.vacumm_avco_svl(qty, svls_to_avco_sync, vacuum_dic)
                    elif update_enabled and "quantity" in vals and svl.quantity < 0.0:
                        svl.update_remaining_avco_svl_in(svls_to_avco_sync)
                    previous_qty = float_round(
                        previous_qty + qty, precision_rounding=precision_qty
                    )
                # Incoming line in layer
                elif f_compare > 0:
                    total_qty = float_round(
                        previous_qty + qty, precision_rounding=precision_qty
                    )
                    # Return moves
                    if update_enabled and (not svl.stock_move_id or svl.stock_move_id.move_orig_ids):
                        svl.update_avco_svl_values(unit_cost=previous_unit_cost)
                    # Normal incoming moves
                    else:
                        unit_cost_processed = True
                        if previous_qty <= 0.0:
                            # Set income svl.unit_cost as previous_unit_cost
                            previous_unit_cost = unit_cost
                        else:
                            previous_unit_cost = svl.get_avco_svl_price(
                                previous_unit_cost,
                                previous_qty,
                                unit_cost,
                                qty,
                                total_qty,
                            )
                        if update_enabled:
                            svl.update_avco_svl_values(remaining_qty=qty)
                    if previous_qty < 0:
                        # Vacuum previous product outs without stock
                        svl.vacumm_avco_svl(qty, svls_to_avco_sync, vacuum_dic)
                    previous_qty = total_qty
                # Outgoing line in layer
                elif f_compare < 0:
                    # Normal OUT
                    if previous_qty <= 0:
                        new_remaining_qty = qty
                    elif previous_qty < abs(qty):
                        new_remaining_qty = float_round(
                            previous_qty + qty, precision_rounding=precision_qty
                        )
                    else:
                        new_remaining_qty = 0.0
                    # Change (svl.remaining_qty - svl.quantity) to previous_qty?
                    vacuum_dic[svl.id].append(
                        (new_remaining_qty - svl.quantity, previous_unit_cost)
                    )
                    if update_enabled:
                        svl.update_avco_svl_values(
                            unit_cost=previous_unit_cost,
                            remaining_qty=new_remaining_qty,
                        )
                    else:
                        # Always update remaning qty?
                        svl.update_avco_svl_values(remaining_qty=new_remaining_qty)
                    previous_qty = float_round(
                        previous_qty + qty, precision_rounding=precision_qty
                    )
                    if update_enabled and "quantity" in vals and svl.quantity < 0:
                        svl.update_remaining_avco_svl_in(svls_to_avco_sync)
                # Manual standard_price adjustment line in layer
                elif not unit_cost and not qty and not svl.stock_move_id:
                    unit_cost_processed = True
                    standard_price = float(svl.description.split(" ")[-1][:-1])
                    # TODO: Review abs in previous_qty or new_diff
                    new_diff = line.currency_id.round(
                        standard_price - previous_unit_cost
                    )
                    adjust_value = line.currency_id.round(new_diff * previous_qty)
                    if svl.value != adjust_value:
                        svl.value = adjust_value
                    previous_unit_cost = standard_price
                # Enable update mode for after lines
                if svl.id == line.id:
                    update_enabled = True
                procesed_lines.add(svl.id)
            # Reprocess svls to set manual adjust values take into account all vacuums
            line.process_avco_svl_manual_adjustements(svls_to_avco_sync, vals)
            # Update product standard price if it is modified
            if float_compare(
                previous_unit_cost,
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).standard_price,
                precision_rounding=line.currency_id.rounding,
            ):
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).sudo().standard_price = previous_unit_cost
            # Compute new values for layer line
            vals_unit_cost = vals.get("unit_cost", line.unit_cost)
            vals.update(
                {
                    "value": line.currency_id.round(
                        vals_unit_cost * vals.get("quantity", line.quantity)
                    ),
                }
            )
            # Update unit_cost for incoming stock moves
            if line.stock_move_id:
                line.stock_move_id.price_unit = vals_unit_cost

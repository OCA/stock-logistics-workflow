# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
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

    def cost_price_avco_sync(self, vals):  # noqa: C901
        procesed_lines = set()
        # precision_price = self.env["decimal.precision"].precision_get("Product Price")
        for line in self.sorted(key=lambda l: (l.create_date, l.id)):
            if (
                line.id in procesed_lines
                or line.product_id.cost_method != "average"
                or line.quantity < 0.0
            ):
                continue
            previous_price = previous_qty = 0.0
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
            inventory_processed = False
            for svl in svls_to_avco_sync:
                if svl.id == line.id:
                    qty = vals.get("quantity", line.quantity)
                    unit_cost = vals.get("unit_cost", line.unit_cost)
                else:
                    qty = svl.quantity
                    unit_cost = svl.unit_cost

                f_compare = float_compare(qty, 0.0, precision_rounding=precision_qty)
                # Incoming line in layer
                if f_compare > 0:
                    total_qty = float_round(
                        previous_qty + qty, precision_rounding=precision_qty
                    )
                    # Return moves or adjust inventory moves
                    if (
                        update_enabled
                        and "quantity" in vals
                        and not inventory_processed
                        and svl.stock_move_id.location_id.usage == "inventory"
                    ):
                        new_svl_qty = svl.quantity - (line.quantity - vals["quantity"])
                        # Check if with the new difference the sign of the move changes
                        if new_svl_qty < 0:
                            location_aux = svl.stock_move_id.location_id
                            svl.stock_move_id.location_id = (
                                svl.stock_move_id.location_dest_id
                            )
                            svl.stock_move_id.location_dest_id = location_aux
                            svl.stock_move_id.move_line_ids.location_id = (
                                svl.stock_move_id.location_id
                            )
                            svl.stock_move_id.move_line_ids.location_dest_id = (
                                svl.stock_move_id.location_dest_id
                            )
                        svl.stock_move_id.quantity_done = abs(new_svl_qty)
                        qty = new_svl_qty
                        inventory_processed = True
                        svl.quantity = new_svl_qty
                        svl.value = svl.quantity * line.currency_id.round(
                            previous_price
                        )
                    if update_enabled and (
                        svl.stock_move_id.move_orig_ids
                        or svl.stock_move_id.inventory_id
                    ):
                        svl.unit_cost = line.currency_id.round(previous_price)
                        svl.value = line.currency_id.round(
                            previous_price * svl.quantity
                        )
                        svl.remaining_value = line.currency_id.round(
                            previous_price * svl.remaining_qty
                        )
                    # Normal incoming moves
                    else:
                        if previous_qty <= 0.0:
                            previous_price = unit_cost
                        else:
                            previous_price = line.currency_id.round(
                                (
                                    (previous_price * previous_qty + unit_cost * qty)
                                    / total_qty
                                )
                                if total_qty
                                else unit_cost
                            )
                    if previous_qty < 0:
                        # Vacuum previous product outs without stock
                        vacuum_qty = qty
                        for svl_to_vacuum in svls_to_avco_sync.filtered(
                            lambda ln: ln.remaining_qty < 0 and ln.quantity < 0.0
                        ):
                            if not svl_to_vacuum.quantity:
                                continue
                            if abs(svl_to_vacuum.remaining_qty) <= vacuum_qty:
                                vacuum_qty += svl_to_vacuum.remaining_qty
                                diff = -svl_to_vacuum.remaining_qty
                                svl_to_vacuum.remaining_qty = 0.0
                            else:
                                svl_to_vacuum.remaining_qty += vacuum_qty
                                diff = vacuum_qty
                                vacuum_qty = 0.0
                            # if svl.id != line.id:
                            svl.remaining_qty = vacuum_qty
                            svl.remaining_value = vacuum_qty * svl.unit_cost
                            new_unit_cost = (
                                (
                                    svl_to_vacuum.unit_cost
                                    * (abs(svl_to_vacuum.quantity + diff))
                                )
                                + previous_price * diff
                            ) / float_round(
                                abs(svl_to_vacuum.quantity),
                                precision_rounding=precision_qty,
                            )
                            new_value = svl_to_vacuum.quantity * new_unit_cost
                            svl_manuals_to_vacuum = svls_to_avco_sync.filtered(
                                lambda ln: ln.unit_cost == 0
                                and ln.quantity == 0.0
                                and not ln.stock_move_id
                                and ln.create_date >= svl_to_vacuum.create_date
                                and ln.create_date <= svl.create_date
                            )
                            for svl_manual in svl_manuals_to_vacuum:
                                # TODO: Compute price instad take of description
                                svl_manual_price = float(
                                    svl_manual.description.split(" ")[-1][:-1]
                                )
                                if svl.currency_id.round(svl_to_vacuum.unit_cost - svl_manual_price):
                                    svl_manual_qty = float_round(
                                        svl_manual.value
                                        / (svl_to_vacuum.unit_cost - svl_manual_price),
                                        precision_rounding=precision_qty,
                                    )
                                    svl_manual_rest = float_round(svl_manual_qty + diff, precision_rounding=precision_qty)
                                    # Set only value of not vaccum quantity
                                    svl_manual.value = svl_manual_rest * svl_manual_price
                            svl_to_vacuum.unit_cost = new_unit_cost
                            svl_to_vacuum.value = new_value
                            svl_to_vacuum.remaining_value = (
                                svl_to_vacuum.remaining_qty * svl_to_vacuum.unit_cost
                            )
                            if vacuum_qty == 0.0:
                                break
                    previous_qty = total_qty
                # Outgoing line in layer
                elif f_compare < 0:
                    if (
                        update_enabled
                        and "quantity" in vals
                        and not inventory_processed
                        and svl.stock_move_id.location_dest_id.usage == "inventory"
                    ):
                        new_svl_qty = svl.quantity + (line.quantity - vals["quantity"])
                        # Check if with the new difference the sign of the move changes
                        if new_svl_qty > 0:
                            location_aux = svl.stock_move_id.location_id
                            svl.stock_move_id.location_id = (
                                svl.stock_move_id.location_dest_id
                            )
                            svl.stock_move_id.location_dest_id = location_aux
                            svl.stock_move_id.move_line_ids.location_id = (
                                svl.stock_move_id.location_id
                            )
                            svl.stock_move_id.move_line_ids.location_dest_id = (
                                svl.stock_move_id.location_dest_id
                            )
                        svl.stock_move_id.quantity_done = abs(new_svl_qty)
                        qty = new_svl_qty
                        inventory_processed = True
                        svl.quantity = new_svl_qty
                        svl.value = svl.quantity * line.currency_id.round(
                            previous_price
                        )
                    else:
                        if previous_qty <= 0:
                            svl.remaining_qty = qty
                        elif previous_qty < abs(qty):
                            svl.remaining_qty = previous_qty + qty
                        else:
                            svl.remaining_qty = 0.0
                        svl.remaining_value = line.currency_id.round(
                            previous_price * svl.remaining_qty
                        )
                    if update_enabled and float_compare(
                        unit_cost, previous_price, precision_rounding=precision_qty,
                    ):
                        svl.unit_cost = line.currency_id.round(previous_price)
                        svl.value = line.currency_id.round(previous_price * qty)
                    previous_qty = float_round(
                        previous_qty + qty, precision_rounding=precision_qty
                    )
                # Manual price adjustment line in layer
                elif not unit_cost and not qty and not svl.stock_move_id:
                    old_diff = svl.value / previous_qty
                    move_diff = previous_price * previous_qty + (
                        (vals.get("unit_cost", line.unit_cost) - line.unit_cost)
                        * (vals.get("quantity", line.quantity))
                    )
                    move_diff_price = move_diff / previous_qty
                    # TODO: Review operations
                    price = previous_price + old_diff + move_diff_price
                    if self.env.context.get("get_price_from_description", True):
                        price = float(svl.description.split(" ")[-1][:-1])
                    if update_enabled:
                        # TODO: Review abs in previous_qty or new_diff
                        new_diff = price - previous_price
                        new_value = line.currency_id.round(new_diff * previous_qty)
                        svl.value = new_value
                        svl.description += _(
                            "\n Product value manually modified (from %s to %s)"
                        ) % (previous_price, price)
                        previous_price = price
                        if not self.env.context.get("force_complete_recompute", True):
                            break
                    # TODO: Avoid duplicate line keeping break and
                    #  previous_price updated
                    previous_price = price
                # Enable update mode for after lines
                if svl.id == line.id:
                    update_enabled = True
                procesed_lines.add(svl.id)
            # Update product standard price if it is modified
            if float_compare(
                previous_price,
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).standard_price,
                precision_rounding=line.currency_id.rounding,
            ):
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).sudo().standard_price = previous_price
            # Compute new values for layer line
            vals_unit_cost = vals.get("unit_cost", line.unit_cost)
            # if "quantity" in vals:
            #     remaining_qty = line.remaining_qty - (line.quantity -
            #                                           vals["quantity"])
            # else:
            #     remaining_qty = line.remaining_qty
            vals.update(
                {
                    "value": line.currency_id.round(
                        vals_unit_cost * vals.get("quantity", line.quantity)
                    ),
                    # "remaining_qty": remaining_qty,
                    # "remaining_value": line.currency_id.round(
                    #     vals_unit_cost * remaining_qty
                    # ),
                }
            )
            # Update unit_cost for incoming stock moves
            if line.stock_move_id:
                line.stock_move_id.price_unit = vals_unit_cost

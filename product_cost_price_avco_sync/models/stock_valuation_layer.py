# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, models
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
        accumulated_qty = 0.0
        accumulated_value = 0.0
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
            vaccum_dic = defaultdict(list)
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
                    # Adjust inventory moves
                    if (
                        update_enabled
                        and "quantity" in vals
                        and not inventory_processed
                        and svl.stock_move_id.location_id.usage == "inventory"
                    ):
                        new_svl_qty = float_round(
                            svl.quantity + (line.quantity - vals["quantity"]),
                            precision_rounding=precision_qty,
                        )
                        # Check if with the new difference the sign of the move changes
                        if (
                            new_svl_qty < 0
                            and svl.stock_move_id.location_id.usage == "inventory"
                        ) or (
                            new_svl_qty > 0
                            and svl.stock_move_id.location_dest_id.usage == "inventory"
                        ):
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
                        # Reasign qty variables
                        qty = new_svl_qty
                        total_qty = float_round(
                            previous_qty + qty, precision_rounding=precision_qty
                        )
                        inventory_processed = True
                        svl.quantity = new_svl_qty
                        svl.unit_cost = line.currency_id.round(previous_price)
                        svl.value = svl.quantity * line.currency_id.round(
                            previous_price
                        )
                        if update_enabled and "quantity" in vals:
                            if new_svl_qty > 0:
                                svl.remaining_qty = new_svl_qty
                            else:
                                svl.remaining_qty = 0.0
                            svl.remaining_value = line.currency_id.round(
                                svl.unit_cost * svl.remaining_qty
                            )
                    # Return moves
                    elif update_enabled and svl.stock_move_id.move_orig_ids:
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
                            previous_price = (
                                unit_cost  # Set previous_price to income svl.unit_cost
                            )
                        else:
                            previous_price = line.currency_id.round(
                                (
                                    (previous_price * previous_qty + unit_cost * qty)
                                    / total_qty
                                )
                                if total_qty
                                else unit_cost
                            )
                        if update_enabled:
                            svl.remaining_qty = qty
                            svl.remaining_value = line.currency_id.round(
                                svl.unit_cost * svl.remaining_qty
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
                                vacuum_qty = float_round(vacuum_qty + svl_to_vacuum.remaining_qty, precision_rounding=precision_qty)
                                diff_qty = -svl_to_vacuum.remaining_qty
                                new_remaining_qty = 0.0
                            else:
                                new_remaining_qty = float_round(
                                    svl_to_vacuum.remaining_qty + vacuum_qty,
                                    precision_rounding=precision_qty
                                )
                                diff_qty = vacuum_qty
                                vacuum_qty = 0.0
                            vaccum_dic[svl_to_vacuum.id].append(
                                (diff_qty, svl.unit_cost)
                            )
                            # if svl.id != line.id:
                            x = 0.0
                            for q, c in vaccum_dic[svl_to_vacuum.id]:
                                x += q * c
                            if new_remaining_qty:
                                x += (
                                    abs(new_remaining_qty)
                                    * vaccum_dic[svl_to_vacuum.id][0][1]
                                )
                            new_unit_cost = x / abs(svl_to_vacuum.quantity)

                            new_value = svl_to_vacuum.quantity * new_unit_cost
                            svl_manuals_to_vacuum = svls_to_avco_sync.filtered(
                                lambda ln: ln.unit_cost == 0
                                and ln.quantity == 0.0
                                and ln.value != 0.0
                                and not ln.stock_move_id
                                and ln.create_date >= svl_to_vacuum.create_date
                                and ln.create_date <= svl.create_date
                            )
                            accumulated_value += (new_value - svl_to_vacuum.value)
                            # Set not last manual value to 0
                            if svl_manuals_to_vacuum:
                                for svl_manuals_to_zero in svl_manuals_to_vacuum[:-1]:
                                    accumulated_value -= svl_manuals_to_zero.value
                                    svl_manuals_to_zero.value = 0.0
                                # svl_manuals_to_vacuum[:-1].value = 0.0
                                last_manual_to_vacuum = svl_manuals_to_vacuum[-1:]
                                price_from_str = float(
                                    last_manual_to_vacuum.description.split(" ")[-1][
                                        :-1
                                    ]
                                )
                                adjust_value = (
                                    price_from_str * accumulated_qty
                                ) - accumulated_value
                                accumulated_value = accumulated_value + (adjust_value - last_manual_to_vacuum.value)
                                # Set last manual value to adjust estimated value
                                last_manual_to_vacuum.value = adjust_value

                            svl_to_vacuum.remaining_qty = new_remaining_qty
                            svl_to_vacuum.remaining_value = (
                                new_remaining_qty * new_unit_cost
                            )
                            svl_to_vacuum.unit_cost = new_unit_cost
                            svl_to_vacuum.value = new_value
                            # Update remaining in incoming line
                            svl.remaining_qty = vacuum_qty
                            svl.remaining_value = vacuum_qty * svl.unit_cost
                            if vacuum_qty == 0.0:
                                break
                    previous_qty = total_qty
                # Outgoing line in layer
                elif f_compare < 0:
                    # Inventory adjustement
                    if (
                        update_enabled
                        and "quantity" in vals
                        and not inventory_processed
                        and svl.stock_move_id.location_dest_id.usage == "inventory"
                    ):
                        new_svl_qty = float_round(
                            svl.quantity + (line.quantity - vals["quantity"]),
                            precision_rounding=precision_qty,
                        )
                        # Check if with the new difference the sign of the move changes
                        if (
                            new_svl_qty < 0
                            and svl.stock_move_id.location_id.usage == "inventory"
                        ) or (
                            new_svl_qty > 0
                            and svl.stock_move_id.location_dest_id.usage == "inventory"
                        ):
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
                        svl.value = line.currency_id.round(
                            svl.quantity * previous_price
                        )
                        if new_svl_qty > 0:
                            svl.remaining_qty = new_svl_qty
                        else:
                            svl.remaining_qty = 0.0
                        svl.remaining_value = line.currency_id.round(
                            previous_price * svl.remaining_qty
                        )
                    else:
                        # Normal OUT
                        if previous_qty <= 0:
                            svl.remaining_qty = qty
                        elif previous_qty < abs(qty):
                            svl.remaining_qty = float_round(
                                previous_qty + qty, precision_rounding=precision_qty
                            )
                        else:
                            svl.remaining_qty = 0.0
                        # Change (svl.remaining_qty - svl.quantity) to previous_qty?
                        vaccum_dic[svl.id].append(
                            (svl.remaining_qty - svl.quantity, previous_price)
                        )
                        # svl.unit_cost = previous_price
                        svl.remaining_value = line.currency_id.round(
                            previous_price * svl.remaining_qty
                        )
                    if 1 or update_enabled and float_compare(
                        unit_cost,
                        previous_price,
                        precision_rounding=precision_qty,
                    ):
                        svl.unit_cost = line.currency_id.round(previous_price)
                        svl.value = line.currency_id.round(previous_price * qty)
                    previous_qty = float_round(
                        previous_qty + qty, precision_rounding=precision_qty
                    )
                    if update_enabled and "quantity" in vals and svl.quantity < 0:
                        svl_out_qty = svl.quantity
                        for svl_in_remaining in svls_to_avco_sync.filtered(
                            lambda ln: ln.remaining_qty > 0
                        ):
                            if abs(svl_out_qty) <= svl_in_remaining.remaining_qty:
                                svl_in_remaining.remaining_qty += svl_out_qty
                                svl_out_qty = 0.0
                            else:
                                svl_out_qty = float_round(svl_out_qty + svl_in_remaining.remaining_qty, precision_rounding=precision_qty)
                                svl_in_remaining.remaining_qty = 0.0
                            svl_in_remaining.remaining_value = line.currency_id.round(
                                svl_in_remaining.remaining_qty * svl_in_remaining.unit_cost
                            )
                            if svl_out_qty == 0.0:
                                break

                # Manual price adjustment line in layer
                elif not unit_cost and not qty and not svl.stock_move_id:
                    # old_diff = svl.value / previous_qty
                    # move_diff = previous_price * previous_qty + (
                    #     (vals.get("unit_cost", line.unit_cost) - line.unit_cost)
                    #     * (vals.get("quantity", line.quantity))
                    # )
                    # move_diff_price = move_diff / previous_qty
                    # TODO: Review operations
                    # price = previous_price + old_diff + move_diff_price
                    if self.env.context.get("get_price_from_description", True):
                        price = float(svl.description.split(" ")[-1][:-1])
                    if 1 or update_enabled:
                        # TODO: Review abs in previous_qty or new_diff
                        new_diff = line.currency_id.round(price - previous_price)
                        new_value = line.currency_id.round(new_diff * previous_qty)
                        if svl.value != new_value:
                            svl.value = new_value
                            # svl.description += _(
                            #     "\n Product value manually modified (from %s to %s)"
                            # ) % (previous_price, price)
                        previous_price = price
                        if not self.env.context.get("force_complete_recompute", True):
                            break
                    # TODO: Avoid duplicate line keeping break and
                    #  previous_price updated
                    previous_price = price
                if 1 or svl.quantity or svl.unit_cost or svl.stock_move_id:
                    if svl.id == line.id:
                        accumulated_qty = float_round(accumulated_qty + vals.get("quantity", line.quantity), precision_rounding=precision_qty)
                        accumulated_value = line.currency_id.round(accumulated_value + vals.get(
                            "unit_cost", line.unit_cost
                        ) * vals.get("quantity", line.quantity))
                        print(
                            "->**Qty:{:.3f} Cost:{:.3f} Value:{:.3f} RemQty:{:.3f}"
                            " Totals: qty:{:.3f} val:{:.3f} avg:{:.3f}".format(
                                vals.get("quantity", line.quantity),
                                vals.get("unit_cost", line.unit_cost),
                                float_round(vals.get("unit_cost", line.unit_cost)
                                * vals.get("quantity", line.quantity), precision_rounding=precision_qty),
                                svl.remaining_qty,
                                accumulated_qty,
                                accumulated_value,
                                line.currency_id.round(accumulated_value / accumulated_qty if accumulated_qty else 0.0)
                            )
                        )
                    else:
                        accumulated_qty = float_round(accumulated_qty + svl.quantity, precision_rounding=precision_qty)
                        accumulated_value = line.currency_id.round(accumulated_value + svl.value)
                        # print(
                        #     "->Qty:{:.3f} Cost:{:.3f} Value:{:.3f} RemQty:{:.3f}"
                        #     " Totals: qty:{:.3f} val:{:.3f} avg:{:.3f}".format(
                        #         svl.quantity,
                        #         svl.unit_cost,
                        #         svl.value,
                        #         svl.remaining_qty,
                        #         accumulated_qty,
                        #         accumulated_value,
                        #         line.currency_id.round(accumulated_value / accumulated_qty if accumulated_qty else 0.0)
                        #     )
                        # )
                # Enable update mode for after lines
                if svl.id == line.id:
                    update_enabled = True
                procesed_lines.add(svl.id)
            # # Reprocess svls to set manual adjust values take into account all vacuums
            # accumulated_qty = accumulated_value = 0.0
            # for svl in svls_to_avco_sync:
            #     if not svl.quantity and not svl.unit_cost and not svl.stock_move_id:
            #         price = float(
            #             svl.description.split(" ")[-1][
            #                 :-1
            #             ]
            #         )
            #         adjust_value = (
            #             price * accumulated_qty
            #         ) - accumulated_value
            #         # Set last manual value to adjust estimated value
            #         if svl.value != adjust_value:
            #             svl.value = adjust_value
            #     if svl.id == line.id:
            #         accumulated_qty = float_round(accumulated_qty + vals.get("quantity", line.quantity), precision_rounding=precision_qty)
            #         accumulated_value = line.currency_id.round(accumulated_value + vals.get(
            #             "unit_cost", line.unit_cost
            #         ) * vals.get("quantity", line.quantity))
            #     else:
            #         accumulated_qty = float_round(accumulated_qty + svl.quantity, precision_rounding=precision_qty)
            #         accumulated_value = line.currency_id.round(accumulated_value + svl.value)

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

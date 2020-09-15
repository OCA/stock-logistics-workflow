# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare, float_round


class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = "stock.valuation.layer"

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
            ("create_date", ">=", self.create_date),
            ("id", "!=", self.id),
        ]
        return (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(domain, order="create_date, id")
        )

    def get_previous_values_avco_sync(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("product_id", "=", self.product_id.id),
            ("create_date", "<=", self.create_date),
            ("id", "!=", self.id),
        ]
        svls = (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(domain, order="create_date, id")
        )
        if not svls:
            return 0.0, 0.0
        previous_price = 0.0
        previous_qty = 0.0
        old_price = 0.0
        for svl in svls:
            # Incoming line in layer
            if svl.quantity > 0.0:
                total_qty = previous_qty + svl.quantity
                previous_price = svl.currency_id.round(
                    (
                        (previous_price * previous_qty + svl.unit_cost * svl.quantity)
                        / total_qty
                    )
                    if total_qty
                    else svl.unit_cost
                )
                old_price = svl.currency_id.round(
                    (
                        (
                                old_price * previous_qty + svl.unit_cost * svl.quantity)
                        / total_qty
                    )
                    if total_qty
                    else svl.unit_cost
                )
                previous_qty = total_qty
            # Outgoing line in layer
            elif svl.quantity < 0.0:
                previous_qty += svl.quantity
            # Manual price adjustment line in layer
            elif not svl.unit_cost and not svl.quantity:
                old_diff = svl.value / previous_qty
                previous_price = old_price + old_diff
        return previous_price, previous_qty

    def _round_value(self, value):
        self.ensure_one()
        return float_round(value, precision_rounding=self.uom_id.rounding)

    def cost_price_avco_sync(self, vals):
        procesed_lines = set()
        for line in self.sorted(key=lambda l: (l.create_date, l.id)):
            if (
                line.id in procesed_lines
                or line.product_id.cost_method != "average"
                or line.quantity <= 0.0
            ):
                continue
            previous_price, previous_qty = line.get_previous_values_avco_sync()
            qty = vals.get("quantity", line.quantity)
            total_qty = previous_qty + qty
            old_price = line.currency_id.round(
                (
                    (previous_price * previous_qty + line.unit_cost * line.quantity)
                    / total_qty
                )
                if total_qty
                else line.unit_cost
            )
            previous_price = line.currency_id.round(
                (
                    (
                        previous_price * previous_qty
                        + vals.get("unit_cost", line.unit_cost) * qty
                    )
                    / total_qty
                )
                if total_qty
                else vals.get("unit_cost", line.unit_cost)
            )
            previous_qty = total_qty
            for svl in line.with_context(skip_avco_sync=True).get_svls_to_avco_sync():
                f_compare = float_compare(
                    svl.quantity, 0.0, precision_rounding=svl.uom_id.rounding
                )
                # Incoming line in layer
                if f_compare > 0:
                    total_qty = previous_qty + svl.quantity
                    previous_price = line.currency_id.round(
                        (
                            (
                                previous_price * previous_qty
                                + svl.unit_cost * svl.quantity
                            )
                            / total_qty
                        )
                        if total_qty
                        else svl.unit_cost
                    )
                    old_price = line.currency_id.round(
                        (
                            (old_price * previous_qty + svl.unit_cost * svl.quantity)
                            / total_qty
                        )
                        if total_qty
                        else svl.unit_cost
                    )
                    previous_qty = total_qty
                # Outgoing line in layer
                elif f_compare < 0:
                    if float_compare(
                        svl.unit_cost,
                        previous_price,
                        precision_rounding=svl.uom_id.rounding,
                    ):
                        svl.with_context(skip_avco_sync=True).write(
                            {
                                "unit_cost": line.currency_id.round(previous_price),
                                "value": line.currency_id.round(
                                    previous_price * svl.quantity
                                ),
                            }
                        )
                        previous_qty += svl.quantity
                # Manual price adjustment line in layer
                elif not svl.unit_cost and not svl.quantity:
                    old_diff = svl.value / previous_qty
                    price = old_price + old_diff
                    new_diff = price - previous_price
                    new_value = line.currency_id.round(new_diff * previous_qty)
                    svl.with_context(skip_avco_sync=True).value = new_value
                    previous_price = price
                    break
            # Update product standard price
            if float_compare(
                previous_price,
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).standard_price,
                precision_rounding=line.currency_id.rounding,
            ):
                line.product_id.with_context(
                    force_company=line.company_id.id
                ).sudo().write({"standard_price": previous_price})
            # Compute new values for layer line
            vals.update(
                {
                    "value": line.currency_id.round(vals["unit_cost"] * line.quantity),
                    "remaining_value": line.currency_id.round(
                        vals["unit_cost"] * line.remaining_qty
                    ),
                }
            )
            # Update price_unit for incoming stock moves
            if line.stock_move_id:
                line.stock_move_id.price_unit = vals["unit_cost"]

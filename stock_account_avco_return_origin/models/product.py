# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.tools import float_compare


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_out_svl_vals(self, quantity, company):
        vals = super()._prepare_out_svl_vals(quantity, company)
        move_id = self.env.context.get("avco_origin_return_move_id")
        if not move_id:
            return vals
        remaining_qty = self.quantity_svl + vals["quantity"]
        if (
            float_compare(remaining_qty, 0, precision_rounding=self.uom_id.rounding)
            <= 0
        ):
            return vals
        move = self.env["stock.move"].browse(move_id)
        unit_cost = move._get_price_unit()
        value = company.currency_id.round(vals["quantity"] * unit_cost)
        rounding_msg = _("Valued at the original receipt price.")
        # A large price gap between receipts can make the origin-price return
        # remove more value than remains on hand, pushing the valuation negative
        # even though stock is still on hand. Cap the removal at the current
        # inventory value so the valuation floors at zero instead of going
        # negative, and realign unit_cost to the capped value.
        if (
            float_compare(
                self.value_svl + value,
                0,
                precision_rounding=company.currency_id.rounding,
            )
            < 0
        ):
            value = -self.value_svl
            unit_cost = company.currency_id.round(value / vals["quantity"])
            rounding_msg = _(
                "Original receipt price would result in negative inventory"
                " valuation; unit cost capped at the remaining inventory"
                " value to keep the valuation non-negative."
            )
        vals["unit_cost"] = unit_cost
        vals["value"] = value
        vals["rounding_adjustment"] = "\n" + rounding_msg
        return vals

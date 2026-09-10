# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    threshold_filter_cost_min = fields.Monetary(
        string="Default Adjustment Cost Threshold",
        currency_field="currency_id",
        help="Default minimum adjustment cost threshold proposed on the "
        "inventory adjustment threshold filter search panel. Leave empty (0) "
        "to start from zero.",
    )
    threshold_filter_qty_diff_min = fields.Float(
        string="Default Quantity Difference Threshold",
        digits="Product Unit of Measure",
        help="Default minimum quantity difference threshold proposed on "
        "the inventory adjustment threshold filter search panel. Leave empty "
        "(0) to start from zero.",
    )

    @api.model
    def get_threshold_filter_defaults(self):
        """Default slider bounds and rounding (as a number of decimal
        digits, like ``field.digits``) proposed on the threshold filter search
        panel, read from ``self.env.company``
        """
        company = self.env.company
        qty_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return {
            "cost_min": company.threshold_filter_cost_min,
            "qty_diff_min": company.threshold_filter_qty_diff_min,
            "cost_digits": company.currency_id.decimal_places,
            "qty_digits": qty_digits,
        }

# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_price_variance_error = fields.Boolean(
        related="company_id.enable_price_variance_error",
        readonly=False,
    )
    price_variance_threshold_percent = fields.Float(
        related="company_id.price_variance_threshold_percent",
        readonly=False,
        help="Maximum variance (in percent) allowable between the product's standard price"
        " and purchase receipt unit price. "
        "Setting this to zero means this threshold will not be checked.",
    )
    price_variance_threshold_amount = fields.Monetary(
        related="company_id.price_variance_threshold_amount",
        readonly=False,
        help="Maximum allowable variance (in monetary amount, based on company currency)"
        " between the product's standard price and the purchase receipt unit price. "
        "Setting this to zero means this threshold will not be checked.",
    )

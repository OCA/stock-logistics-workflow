# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    enable_price_variance_error = fields.Boolean()
    price_variance_threshold_percent = fields.Float(
        help="Maximum variance (in percent) allowable between the product's standard price"
        " and purchase receipt unit price."
        "Setting this to zero means this threshold will not be checked."
    )
    price_variance_threshold_amount = fields.Monetary(
        help="Maximum allowable variance (in monetary amount, based on company currency)"
        " between the product's standard price and the purchase receipt unit price."
        "Setting this to zero means this threshold will not be checked."
    )

    @api.constrains(
        "price_variance_threshold_percent", "price_variance_threshold_amount"
    )
    def _check_price_variance_threshold(self):
        for rec in self:
            if (
                rec.price_variance_threshold_percent < 0
                or rec.price_variance_threshold_amount < 0
            ):
                raise ValidationError(_("The threshold values cannot be negative."))

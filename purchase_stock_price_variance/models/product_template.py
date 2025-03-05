# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    price_variance_threshold_percent = fields.Float(
        help="Maximum variance (in percent) allowable between the product's standard price"
        " and purchase receipt unit price. "
        "Setting this to zero means the threshold will refer to the global setting."
    )
    price_variance_threshold_amount = fields.Monetary(
        help="Maximum allowable variance (in monetary amount, based on company currency)"
        " between the product's standard price and the purchase receipt unit price. "
        "Setting this to zero means the threshold will refer to the global setting."
    )
    bypass_price_variance_check = fields.Boolean(
        copy=False,
        tracking=True,
        help="If enabled, this product will not raise an error for price variance between "
        "the product's standard price and the purchase receipt unit price.",
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

    def write(self, vals):
        if "bypass_price_variance_check" in vals:
            if not self.env.user.has_group(
                "purchase_stock_price_variance.group_manage_price_variance_check"
            ):
                raise UserError(
                    _(
                        "You do not have permission to modify the "
                        "'Bypass Price Variance Check' field. "
                        "Please contact an administrator or a user "
                        "with the appropriate permissions."
                    )
                )
        return super().write(vals)

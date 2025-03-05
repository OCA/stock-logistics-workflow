# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = "product.category"

    bypass_price_variance_check = fields.Boolean(
        copy=False,
        tracking=True,
        help="If enabled, the products under this category will not raise an error for price"
        " variance between the product's standard price and the purchase receipt unit price.",
    )

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

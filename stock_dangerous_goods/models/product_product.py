# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_lq_product = fields.Boolean(
        compute="_compute_is_lq_product",
        help="Whether this product is a Limited Quantity product or not",
    )

    @api.depends("limited_amount_id", "is_dangerous")
    def _compute_is_lq_product(self):
        limited_amount_lq = self.env.ref(
            "l10n_eu_product_adr_dangerous_goods.limited_amount_1"
        )
        for record in self:
            record.is_lq_product = (
                record.is_dangerous and record.limited_amount_id == limited_amount_lq
            )

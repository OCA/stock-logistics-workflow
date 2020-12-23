# Copyright 2020 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_has_both_assortment_id = fields.Many2one(
        related="product_id", string="Product with whitelist and blacklist"
    )
    product_has_blacklist_assortment_id = fields.Many2one(
        related="product_id", string="Product with blacklist"
    )

    @api.onchange(
        "product_has_both_assortment_id", "product_has_blacklist_assortment_id"
    )
    def _onchange_product_secondary_fields(self):
        if self.product_has_both_assortment_id:
            self.product_id = self.product_has_both_assortment_id
        if self.product_has_blacklist_assortment_id:
            self.product_id = self.product_has_blacklist_assortment_id

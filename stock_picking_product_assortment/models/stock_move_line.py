# Copyright 2020 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


# We overwrite this class as a trick to repeat the product_id field with different
# attributes on the view.
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    assortment_product_id = fields.Many2one(
        related="product_id", string="Product with blacklist"
    )

    @api.onchange("assortment_product_id")
    def _onchange_product_secondary_fields(self):
        if self.assortment_product_id:
            self.product_id = self.assortment_product_id

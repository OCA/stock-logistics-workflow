# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    has_lq_products = fields.Boolean(compute="_compute_has_lq_products")

    @api.depends("quant_ids.product_id.is_lq_product")
    def _compute_has_lq_products(self):
        for record in self:
            record.has_lq_products = record._has_lq_products()

    def _has_lq_products(self):
        self.ensure_one()
        for quant in self.quant_ids:
            if quant.product_id.is_lq_product:
                return True
        return False

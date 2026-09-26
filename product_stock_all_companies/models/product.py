# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_by_company_ids = fields.Many2many(
        "stock.company",
        compute_sudo=True,
        compute="_compute_stock_by_company_ids",
    )

    @api.depends("qty_available")
    def _compute_stock_by_company_ids(self):
        StockCompany = self.env["stock.company"].sudo()
        StockCompany._calculate_stock_for_product(self)
        for product in self:
            records = StockCompany.search([("product_id", "=", product.id)])
            product.stock_by_company_ids = records

# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class StockCompany(models.Model):
    _name = "stock.company"
    _description = "stock.company"

    product_id = fields.Many2one("product.product")
    company_id = fields.Many2one("res.company")
    quantity_available = fields.Float(digits="Product Unit of Measure")
    uom_id = fields.Many2one(related="product_id.uom_id")

    def _calculate_stock_for_product(self, product):
        companies = self.env["res.company"].search([])
        for company in companies:
            qty = product.with_context(allowed_company_ids=[company.id]).qty_available

            record = self.search(
                [
                    ("product_id", "=", product.id),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )

            if record:
                record.quantity_available = qty
            else:
                self.create(
                    {
                        "product_id": product.id,
                        "company_id": company.id,
                        "quantity_available": qty,
                    }
                )

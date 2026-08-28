# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_by_company_ids = fields.Many2many(
        "stock.company",
        compute="_compute_stock_by_company_template",
    )

    @api.depends("product_variant_ids.stock_by_company_ids", "product_variant_count")
    def _compute_stock_by_company_template(self):
        for template in self:
            if template.product_variant_count <= 1 and template.type == "consu":
                template.stock_by_company_ids = (
                    template.product_variant_ids.stock_by_company_ids
                )
            else:
                template.stock_by_company_ids = False

# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    landed_cost_specific = fields.Boolean(
        string="Specific landed costs?", default=False
    )

    product_tmpl_landed_cost_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_landed_cost_rel",
        column1="product_template_id",
        column2="product_landed_cost_id",
    )

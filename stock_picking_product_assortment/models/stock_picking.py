# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2023 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = "stock.picking"

    assortment_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Assortment Products",
        compute="_compute_product_assortment_ids",
    )
    has_assortment = fields.Boolean(compute="_compute_product_assortment_ids")

    @api.depends("partner_id")
    def _compute_product_assortment_ids(self):
        # If we don't initialize the fields we get an error with NewId
        self.assortment_product_ids = self.env["product.product"]
        self.has_assortment = False
        product_domain = []
        partners = self.partner_id + self.partner_id.parent_id
        if partners:
            for ir_filter in partners.applied_assortment_ids:
                product_domain = expression.AND(
                    [product_domain, ir_filter._get_eval_domain()]
                )
            if product_domain:
                self.assortment_product_ids = self.env["product.product"].search(
                    product_domain
                )
                self.has_assortment = True

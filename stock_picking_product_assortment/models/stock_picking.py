# Copyright 2020 Tecnativa - Carlos Roca
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
        for record in self:
            if record.partner_id and record.picking_type_id.code == "outgoing":
                # As all_partner_ids can't be a stored field
                filters = self.env["ir.filters"].search(
                    [
                        (
                            "all_partner_ids",
                            "in",
                            (self.partner_id + self.partner_id.parent_id).ids,
                        ),
                    ]
                )
                domain = []
                for fil in filters:
                    domain = expression.AND([domain, fil._get_eval_domain()])
                self.has_assortment = True
                self.assortment_product_ids = self.env["product.product"].search(domain)

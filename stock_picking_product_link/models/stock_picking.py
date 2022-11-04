# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    product_ids = fields.Many2many(
        string="Products",
        comodel_name="product.product",
        compute="_compute_product_ids",
    )
    product_count = fields.Integer(
        string="Number of Products",
        compute="_compute_product_ids",
    )

    @api.depends("move_line_ids", "move_line_ids.product_id")
    @api.model
    def _compute_product_ids(self):
        for picking in self:
            move_products = picking.move_line_ids.mapped("product_id")
            move_wo_package_products = picking.move_ids_without_package.mapped(
                "product_id"
            )
            products = move_products + move_wo_package_products
            picking.product_count = len(set(products.ids))
            picking.product_ids = products

    def action_view_products(self):
        self.ensure_one()
        return {
            "name": _("Products"),
            "view_mode": "tree,form",
            "res_model": "product.product",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.product_ids.ids)],
        }

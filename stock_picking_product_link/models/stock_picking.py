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
    product_template_ids = fields.Many2many(
        string="Product Templates",
        comodel_name="product.template",
        compute="_compute_product_ids",
    )
    product_count = fields.Integer(
        string="Number of Products",
        compute="_compute_product_ids",
        help="""This displays the amount of products (variants) in the stock transfer.
            The amount of product templates may be lower.""",
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
            picking.product_template_ids = products.mapped("product_tmpl_id")

    def action_view_products(self):
        self.ensure_one()
        if self.env.user.has_group("product.group_product_variant"):
            return {
                "name": _("Products"),
                "view_mode": "tree,form",
                "res_model": "product.product",
                "type": "ir.actions.act_window",
                "domain": [("id", "in", self.product_ids.ids)],
            }
        # The use case for returning a list of product templates here is that
        # clients who have not enabled product variants are not
        # functionality-wise familiar with product variants. The fields and
        # available interactions are slightly different.
        else:
            return {
                "name": _("Products"),
                "view_mode": "tree,form",
                "res_model": "product.template",
                "type": "ir.actions.act_window",
                "domain": [("id", "in", self.product_template_ids.ids)],
            }

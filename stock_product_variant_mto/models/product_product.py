# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields

IS_MTO_HELP = """
    Check or Uncheck this field to enable the Make To Order on the variant,
    independantly from its template configuration.\n
    Please note that activating or deactivating Make To Order on the template,
    will reset this setting on its variants.
"""

class ProductProduct(models.Model):
    _inherit = "product.product"

    is_mto = fields.Boolean(
        string="Variant is MTO",
        compute="_compute_is_mto",
        store=True,
        readonly=False,
        help=IS_MTO_HELP,
    )

    route_ids = fields.Many2many(
        "stock.location.route",
        compute="_compute_route_ids",
        domain="[('product_selectable', '=', True)]",
        store=False
    )

    def _compute_is_mto(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        for product in self:
            if not mto_route:
                product.is_mto = False
                continue
            product.is_mto = mto_route in product.product_tmpl_id.route_ids

    @api.depends("is_mto", "product_tmpl_id.route_ids")
    def _compute_route_ids(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        for product in self:
            if mto_route and mto_route in product.product_tmpl_id.route_ids:
                if not product.is_mto:
                    product.route_ids = product.product_tmpl_id.route_ids - mto_route
                    continue
            else:
                if mto_route and product.is_mto:
                    product.route_ids = product.product_tmpl_id.route_ids + mto_route
                    continue
            product.route_ids = product.product_tmpl_id.route_ids

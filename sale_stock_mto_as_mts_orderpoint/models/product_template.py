# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def write(self, vals):
        # Archive orderpoints when MTO route is removed
        if "route_ids" not in vals:
            return super().write(vals)
        mto_products = self._filter_mto_products()
        res = super().write(vals)
        not_mto_products = self._filter_mto_products(mto=False)
        # products to update are the intersection of both recordsets
        products_to_update = mto_products & not_mto_products
        if products_to_update:
            products_to_update._archive_orderpoints_on_mto_removal()
        return res

    def _filter_mto_products(self, mto=True):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if mto:
            func = lambda p: mto_route in p.route_ids  # noqa
        else:
            func = lambda p: mto_route not in p.route_ids  # noqa
        return self.filtered(func)

    def _get_orderpoints_to_archive_domain(self):
        warehouses = self.env["stock.warehouse"].search([])
        locations = warehouses._get_locations_for_mto_orderpoints()
        return [
            ("product_id", "in", self.mapped("product_variant_ids").ids),
            ("product_min_qty", "=", 0.0),
            ("product_max_qty", "=", 0.0),
            ("location_id", "in", locations.ids),
        ]

    def _archive_orderpoints_on_mto_removal(self):
        domain = self._get_orderpoints_to_archive_domain()
        ops = self.env["stock.warehouse.orderpoint"].search(domain)
        if ops:
            ops.write({"active": False})

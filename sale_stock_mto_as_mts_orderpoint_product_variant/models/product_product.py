# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models

class ProductProduct(models.Model):
    _inherit = "product.product"

    def _variant_is_mto(self):
        self.ensure_one()
        return self.is_mto

    def _inverse_is_mto(self):
        res = super()._inverse_is_mto()
        self._archive_orderpoints_on_mto_removal()
        return res

    @api.depends("product_tmpl_id.route_ids")
    def _compute_is_mto(self):
        # Archive orderpoints when variant becomes not mto
        res = super()._compute_is_mto()
        self._archive_orderpoints_on_mto_removal()
        return res

    def _get_orderpoints_to_archive_domain(self):
        # Orderpoints to archive are those where
        warehouses = self.env["stock.warehouse"].search([])
        locations = warehouses._get_locations_for_mto_orderpoints()
        return [
            ("product_id", "in", self.ids),
            ("product_min_qty", "=", 0.0),
            ("product_max_qty", "=", 0.0),
            ("location_id", "in", locations.ids),
            ("product_id.is_mto", "=", False),
        ]

    def _archive_orderpoints_on_mto_removal(self):
        domain = self._get_orderpoints_to_archive_domain()
        ops = self.env["stock.warehouse.orderpoint"].search(domain)
        if ops:
            ops.write({"active": False})

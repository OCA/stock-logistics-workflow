# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.osv.expression import AND


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _variant_is_mto(self):
        self.ensure_one()
        return self.is_mto

    def write(self, vals):
        res = super().write(vals)
        if "is_mto" in vals and vals["is_mto"] == False:
            self._archive_orderpoints_on_mto_removal()
        return res

    def _get_orderpoints_to_archive_domain(self, warehouse):
        # Orderpoints to archive are those where
        domain = warehouse._get_orderpoints_to_archive_domain()
        if self:
            domain = AND(
                [
                    domain,
                    [("product_id", "in", self.ids)],
                ]
            )
        return domain

    def _archive_orderpoints_on_mto_removal(self):
        warehouses = self.env["stock.warehouse"].search([])
        for wh in warehouses:
            domain = self._get_orderpoints_to_archive_domain(wh)
            ops = self.env["stock.warehouse.orderpoint"].search(domain)
            if ops:
                ops.write({"active": False})

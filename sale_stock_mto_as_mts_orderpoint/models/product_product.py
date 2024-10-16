# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

class ProductProduct(models.Model):
    _inherit = "product.product"

    def _variant_is_mto(self):
        self.ensure_one()
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        return mto_route in self.route_ids

    def _variant_is_not_mto(self):
        return not self._variant_is_mto()

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def _is_mto(self):
        self.ensure_one()
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        return mto_route in self.route_ids

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()
        picking_type = self.mapped("picking_type_id")
        if picking_type.shipping_policy == "force_as_soon_as_possible":
            res["move_type"] = "direct"
        elif picking_type.shipping_policy == "force_all_products_ready":
            res["move_type"] = "one"
        return res

# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _shipping_policy_from_picking_type(self):
        picking_type = self.mapped("picking_type_id")
        if picking_type.shipping_policy == "force_as_soon_as_possible":
            return "direct"
        elif picking_type.shipping_policy == "force_all_products_ready":
            return "one"
        return None

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()
        picking_type_move_type = self._shipping_policy_from_picking_type()
        if picking_type_move_type:
            res["move_type"] = picking_type_move_type
        return res

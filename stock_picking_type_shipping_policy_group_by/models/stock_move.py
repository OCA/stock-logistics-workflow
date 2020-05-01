# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _domain_search_picking_handle_move_type(self):
        picking_type_move_type = self._shipping_policy_from_picking_type()
        if picking_type_move_type:
            return [("move_type", "=", picking_type_move_type)]
        else:
            return super()._domain_search_picking_handle_move_type()

# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _cal_move_weight(self):
        # Override method from `delivery` module to compute a more accurate
        # weight from the product packaging.
        for move in self:
            move.weight = move.product_id.get_total_weight_from_packaging(
                move.product_qty
            )

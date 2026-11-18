# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_out_svl_vals(self, forced_quantity):
        return_moves = self.filtered(lambda m: m.origin_returned_move_id)
        other_moves = self - return_moves
        svl_vals_list = (
            super(StockMove, other_moves)._get_out_svl_vals(forced_quantity)
            if other_moves
            else []
        )
        for move in return_moves:
            svl_vals_list += super(
                StockMove,
                move.with_context(origin_returned_move=move.origin_returned_move_id),
            )._get_out_svl_vals(forced_quantity)
        return svl_vals_list

# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_out_svl(self, forced_quantity=None):
        return_moves = self.filtered(lambda m: m.origin_returned_move_id)
        other_moves = self - return_moves
        res = self.env["stock.valuation.layer"].sudo()
        if other_moves:
            res |= super(StockMove, other_moves)._create_out_svl(forced_quantity)
        for move in return_moves:
            res |= super(
                StockMove,
                move.with_context(origin_returned_move=move.origin_returned_move_id),
            )._create_out_svl(forced_quantity)
        return res

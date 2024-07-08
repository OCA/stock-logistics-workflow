# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        origin_returned_moves = self.browse()
        for move in self:
            if move._is_out():
                origin_returned_moves |= move.origin_returned_move_id
        # We cannot assign origin returned move context to individual moves, therefore
        # assign them all to self
        if origin_returned_moves:
            self = self.with_context(origin_returned_moves=origin_returned_moves)
        return super()._action_done(cancel_backorder)

# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        moves = super()._action_done(cancel_backorder=cancel_backorder)
        if moves and moves[:1].picking_code in ("outgoing", "internal"):
            return moves
        for move_line in moves.mapped("move_line_ids"):
            if move_line._skip_lot_price_unit_update():
                continue
            move_line.lot_id.price_unit = move_line.move_id.price_unit
        return moves

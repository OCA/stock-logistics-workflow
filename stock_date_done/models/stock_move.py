# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            picking = move.picking_id
            if (
                picking.state == "done"
                and picking.date_done
                and move.date != picking.date_done
            ):
                move.date = picking.date_done
        return moves

    def _create_account_move(self):
        if self.env.context.get("force_period_date"):
            return super()._create_account_move()
        moves_by_date = defaultdict(lambda: self.browse())
        for move in self:
            date_done = move.picking_id.date_done or move.scrap_id.date_done
            period_date = (
                fields.Date.context_today(move, date_done) if date_done else False
            )
            moves_by_date[period_date] |= move
        account_moves = self.env["account.move"]
        for period_date, moves in moves_by_date.items():
            if period_date:
                moves = moves.with_context(force_period_date=period_date)
            account_moves |= super(StockMove, moves)._create_account_move()
        return account_moves

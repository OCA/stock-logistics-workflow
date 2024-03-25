# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2016 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.fields import first

from ..utils import check_date


class StockMove(models.Model):
    _inherit = "stock.move"

    def _backdating_account_moves(self):
        """Set date on linked account.move same for each move in `self`."""
        picking_account_moves = self.env["account.move"].search(
            [
                ("stock_move_id", "in", self.ids),
            ],
        )
        for stock_move in self:
            move_account_moves = picking_account_moves.filtered(
                lambda am: am.stock_move_id == stock_move
            )
            move_account_moves.update(
                {
                    "name": False,
                    "date": stock_move.date.date(),
                }
            )

    def _backdating_action_done(self, moves_todo):
        """Process the moves one by one, backdating the ones that need to."""
        moves_todo_ids = set(moves_todo.ids)
        for move in self:
            move_line = first(move.move_line_ids)
            date_backdating = move_line.date_backdating
            if date_backdating:
                move = move.with_context(
                    date_backdating=date_backdating,
                )

            move_todo = super(StockMove, move)._action_done()
            moves_todo_ids.update(move_todo.ids)

            # overwrite date field where applicable
            date_backdating = move_line.date_backdating
            if date_backdating:
                check_date(date_backdating)
                move.date = date_backdating
                move.move_line_ids.update(
                    {
                        "date": date_backdating,
                    }
                )
        return self.browse(moves_todo_ids)

    def _action_done(self, cancel_backorder=False):
        moves_todo = self.env["stock.move"]
        has_move_lines_to_backdate = any(self.mapped("move_line_ids.date_backdating"))
        if not has_move_lines_to_backdate:
            moves_todo |= super()._action_done(cancel_backorder=cancel_backorder)
        else:
            moves_todo = self._backdating_action_done(moves_todo)
        return moves_todo

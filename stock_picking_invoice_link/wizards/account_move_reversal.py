# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        """Link return moves to the lines of refund invoice"""
        action = super().reverse_moves()
        if "res_id" in action:
            moves = self.env["account.move"].browse(action["res_id"])
        else:
            moves = self.env["account.move"].search(action["domain"])
        for line in moves.mapped("invoice_line_ids"):
            reverse_moves = line.move_line_ids.mapped("returned_move_ids")
            if reverse_moves:
                line.move_line_ids = reverse_moves
        return action

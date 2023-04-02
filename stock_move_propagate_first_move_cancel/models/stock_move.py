# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_cancel(self):
        res = super()._action_cancel()
        moves_to_cancel = self.search(
            [("first_move_id", "in", self.ids), ("id", "not in", self.ids)]
        )
        if moves_to_cancel:
            return moves_to_cancel._action_cancel()
        return res

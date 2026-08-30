# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _action_cancel(self):
        res = super()._action_cancel()
        # This will avoid recursion in some flows
        already_cancel_ids = self.env.context.get("first_move_cancelled_ids", [])
        moves_to_cancel = self.search(
            [
                ("first_move_id", "in", self.ids),
                ("id", "not in", self.ids),
                ("id", "not in", already_cancel_ids),
                ("state", "not in", ("cancel", "done")),
            ]
        )
        if moves_to_cancel:
            return moves_to_cancel.with_context(
                first_move_cancelled_ids=moves_to_cancel.ids
            )._action_cancel()
        return res

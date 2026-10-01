# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        # Override to add a context key to know into the recompute
        # putaway call that it is called from the assign method
        # This is required since the recompute putaway method is called
        # from the write method of the stock.move.line model when
        # assigning a package level move line. In that case, we don't want
        # to clear the putaway_deferred flag since the operator has not
        # set a destination on the move line.
        self_in_action_assign = self.with_context(in_action_assign=True)
        return super(StockMove, self_in_action_assign)._action_assign(
            force_qty=force_qty
        )

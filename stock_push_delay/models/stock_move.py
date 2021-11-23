# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _push_apply(self):
        """Manual triggering"""
        if self.env.context.get("manual_push", False):
            new_move = super(StockMove, self)._push_apply()
            if new_move:
                new_move._action_confirm()
            return new_move
        return self.env["stock.move"]

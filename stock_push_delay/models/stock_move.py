# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _push_apply(self):
        """Manual triggering"""
        if self.env.context.get("manual_push", False):
            return super(StockMove, self)._push_apply()

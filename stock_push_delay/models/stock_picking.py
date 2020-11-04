# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self.with_context(manual_push=True):
            picking.move_lines._push_apply()
        return res

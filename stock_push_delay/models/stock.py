# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _push_apply(self):
        """Manual triggering"""
        if self.env.context.get('manual_push', False):
            return super(StockMove, self)._push_apply()


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self.with_context(manual_push=True):
            picking.move_lines._push_apply()
        return res

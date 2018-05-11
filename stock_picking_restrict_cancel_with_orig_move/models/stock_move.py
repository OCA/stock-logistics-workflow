# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _action_cancel(self):
        if (self.env.context.get('bypass_check_state') or
                all(move.state in ('cancel', 'done')
                    for move in self.mapped('move_orig_ids'))):
            return super(StockMove, self.with_context(
                bypass_check_state=True))._action_cancel()
        else:
            pickings = self.env['stock.picking']
            for move in self:
                for orig_stock_move in move.move_orig_ids:
                    pickings |= orig_stock_move.picking_id
            raise UserError(
                _("Cancelation of destination move is restricted if any "
                  "previous move is not canceled or done."
                  "Original moves are not canceled or done on the following "
                  "pickings : %s") % ', '.join([p.name for p in pickings]))

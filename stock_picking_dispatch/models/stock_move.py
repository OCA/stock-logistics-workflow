# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import fields, models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    dispatch_id = fields.Many2one(
        'picking.dispatch', 'Dispatch', index=True, copy=False,
        help='who this move is dispatched to'
    )

    def action_cancel(self):
        """
        in addition to what the method in the parent class does,
        cancel the dispatches for which all moves where cancelled
        """
        _logger.debug('cancel stock.moves %s', self.ids)
        status = super(StockMove, self).action_cancel()

        if self.ids:
            dispatches = self.env['picking.dispatch']
            for move in self:
                if move.dispatch_id:
                    dispatches |= move.dispatch_id

            # Keep on picking_dispatch which all moves canceled
            dispatches.filtered(
                lambda d: all(m.state == 'cancel' for m in d.move_ids)
            )
            if dispatches:
                _logger.debug('set state to cancel for picking.dispatch %s',
                              list(dispatches))
                dispatches.write({'state': 'cancel'})

        return status

    def action_done(self):
        """
        in addition to the parent method does, set the dispatch done if all
        moves are done or canceled
        """
        _logger.debug('done stock.moves %s', self.ids)
        status = super(StockMove, self).action_done()
        if self.ids:
            dispatches = self.env['picking.dispatch']
            for move in self:
                if move.dispatch_id:
                    dispatches |= move.dispatch_id
            dispatches.check_finished()
        return status

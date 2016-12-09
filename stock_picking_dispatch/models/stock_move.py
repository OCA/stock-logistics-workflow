# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    dispatch_id = fields.Many2one(
        'picking.dispatch', 'Dispatch', index=True, copy=False,
        help='In which picking dispatch this move will be processed.'
    )

    @api.multi
    def action_cancel(self):
        """
        in addition to what the method in the parent class does,
        cancel the dispatches for which all moves where cancelled
        """
        _logger.debug('cancel stock.moves %s', self.ids)
        status = super(StockMove, self).action_cancel()

        if self.ids:
            dispatches = self.mapped('dispatch_id')

            # Keep on picking_dispatch which all moves canceled
            dispatches.filtered(
                lambda d: all(m.state == 'cancel' for m in d.move_ids)
            )
            if dispatches:
                _logger.debug('set state to cancel for picking.dispatch %s',
                              list(dispatches))
                dispatches.write({'state': 'cancel'})

        return status

    @api.multi
    def action_done(self):
        """
        in addition to the parent method does, set the dispatch done if all
        moves are done or canceled
        """
        _logger.debug('done stock.moves %s', self.ids)
        status = super(StockMove, self).action_done()
        if self.ids:
            dispatches = self.mapped('dispatch_id')
            if dispatches:
                dispatches.check_finished()
        return status

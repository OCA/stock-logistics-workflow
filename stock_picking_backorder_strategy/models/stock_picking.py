# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def action_done(self):
        return super(StockPicking, self.with_context(on_picking_validation=True)).action_done()

    @api.multi
    def _check_backorder(self):
        self.ensure_one()
        # If strategy == 'manual', let the normal process going on
        if self.picking_type_id.backorder_strategy == 'manual':
            return super(StockPicking, self)._check_backorder()
        return False

    @api.multi
    def _create_backorder(self, backorder_moves=None):
        if backorder_moves is None:
            backorder_moves = []
        res = False
        # Do nothing with pickings 'no_create'
        pickings = self.filtered(
            #The pickings we want to keep creating a backorder are the ones
            #with a backorder strategy set to anything other than 'no_create'
            #or the ones which we only want to skip backorder if we are validating the picking
            #as a whole, but we are not on such context (validating only a stock move, for example).
            lambda p: (p.picking_type_id.backorder_strategy != 'no_create') or\
                (p.picking_type_id.disable_backorder_only_on_picking_validation and not self._context.get('on_picking_validation'))
        )
        pickings_no_create = self - pickings
        pickings_no_create.mapped('move_lines')._cancel_remaining_quantities()
        res = super(StockPicking, pickings)._create_backorder(
            backorder_moves=backorder_moves)
        to_cancel = res.filtered(
            lambda b: b.backorder_id.picking_type_id.backorder_strategy ==
            'cancel')
        to_cancel.action_cancel()
        return res

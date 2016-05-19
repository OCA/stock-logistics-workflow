# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class StockMove(orm.Model):
    _inherit = 'stock.move'
    _columns = {
        'dispatch_id': fields.many2one(
            'picking.dispatch', 'Dispatch',
            select=True,
            help='who this move is dispatched to'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default['dispatch_id'] = False
        return super(StockMove, self).\
            copy_data(cr, uid, id, default=default, context=context)

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """
        in addition to what the original method does, create backorder
        picking.dispatches and set the state of picing.dispatch
        according to the state of moves state
        """
        move_obj = self.pool.get('stock.move')
        dispatch_obj = self.pool.get('picking.dispatch')
        _logger.debug('partial stock.moves %s %s', ids, partial_datas)
        complete_move_ids = super(StockMove, self).do_partial(cr, uid, ids,
                                                              partial_datas,
                                                              context)
        # in complete_move_ids, we have:
        # * moves that were fully processed
        # * newly created moves (the processed part of partially processed
        #   moves) belonging to the same dispatch as the original move
        # so the difference between the original set of moves and the
        # complete_moves is the set of unprocessed moves
        unprocessed_move_ids = set(ids) - set(complete_move_ids)
        _logger.debug(
            'partial stock.moves: complete_move_ids %s, '
            'unprocessed_move_ids %s',
            complete_move_ids, unprocessed_move_ids)
        # unprocessed moves are still linked to the dispatch : this dispatch
        # must not be marked as Done
        unfinished_dispatch_ids = {}
        for move in move_obj.browse(cr, uid, list(unprocessed_move_ids),
                                    context=context):
            if not move.dispatch_id:
                continue
            # value will be set later to a new dispatch
            unfinished_dispatch_ids[move.dispatch_id.id] = None
        maybe_finished_dispatches = {}
        for move in move_obj.browse(cr, uid, complete_move_ids,
                                    context=context):
            if not move.dispatch_id:
                continue
            dispatch_id = move.dispatch_id.id
            if dispatch_id in unfinished_dispatch_ids:
                # the dispatch was partially processed: we need to link the
                # move to a new dispatch containing only fully processed moves
                if unfinished_dispatch_ids[dispatch_id] is None:
                    # create a new dispatch, and record its id
                    _logger.debug(
                        'create backorder picking.dispatch of %s', dispatch_id)
                    new_dispatch_id = dispatch_obj.copy(cr, uid, dispatch_id, {
                        'backorder_id': dispatch_id,
                    })
                    unfinished_dispatch_ids[dispatch_id] = new_dispatch_id
                dispatch_id = unfinished_dispatch_ids[dispatch_id]
            maybe_finished_dispatches.setdefault(
                dispatch_id, []).append(move.id)
        for dispatch_id, move_ids in maybe_finished_dispatches.iteritems():
            move_obj.write(cr, uid, move_ids, {'dispatch_id': dispatch_id})
        dispatch_obj.check_finished(
            cr, uid, list(maybe_finished_dispatches), context)
        dispatch_obj.write(
            cr, uid, list(unfinished_dispatch_ids), {'state': 'assigned'})
        return complete_move_ids

    def action_cancel(self, cr, uid, ids, context=None):
        """
        in addition to what the method in the parent class does,
        cancel the dispatches for which all moves where cancelled
        """
        _logger.debug('cancel stock.moves %s', ids)
        status = super(StockMove, self).action_cancel(cr, uid, ids, context)
        if not ids:
            return True
        dispatch_obj = self.pool.get('picking.dispatch')
        dispatches = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.dispatch_id:
                dispatches.add(move.dispatch_id.id)
        for dispatch in dispatch_obj.browse(cr, uid, list(dispatches),
                                            context=context):
            if any(move.state != 'cancel' for move in dispatch.move_ids):
                dispatches.remove(dispatch.id)
        if dispatches:
            _logger.debug(
                'set state to cancel for picking.dispatch %s',
                list(dispatches))
            dispatch_obj.write(
                cr, uid, list(dispatches), {'state': 'cancel'}, context)
        return status

    def action_done(self, cr, uid, ids, context=None):
        """
        in addition to the parent method does, set the dispatch done if all
        moves are done or canceled
        """
        _logger.debug('done stock.moves %s', ids)
        status = super(StockMove, self).action_done(cr, uid, ids, context)
        if not ids:
            return True
        dispatch_obj = self.pool.get('picking.dispatch')
        dispatches = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.dispatch_id:
                dispatches.add(move.dispatch_id.id)
        dispatch_obj.check_finished(cr, uid, list(dispatches), context)
        return status

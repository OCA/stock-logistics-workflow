# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from datetime import datetime
from openerp.osv.orm import Model
from openerp.osv import osv, fields
from openerp.osv.osv import except_osv
from tools.translate import _

_logger = logging.getLogger(__name__)

class PickingDispatch(Model):
    """New object that contain stock moves selected from stock.picking by the warehouse
    manager so that the warehouseman can go and bring the product where they're asked for.
    The purpose is to know who will look for what in the warehouse. We don't use the
    stock.picking object cause we don't want to break the relation with the SO and all
    related workflow.
    This object is designed for the warehouse problematics and must help the people there
    to organize their work."""

    _name = 'picking.dispatch'
    _description = "Dispatch Picking Order"

    def _get_related_picking(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        if not ids:
            return result
        for dispatch_id in ids:
            result[dispatch_id] = []
        sql = ("SELECT sm.dispatch_id, sm.picking_id FROM stock_move sm "
              "WHERE sm.dispatch_id in %s AND sm.picking_id is NOT NULL")
        cr.execute(sql, (tuple(ids),))
        res = cr.fetchall()
        for line in res:
            result[line[0]].append(line[1])
        return result

    _columns  = {
        'name': fields.char('Name', size=64, required=True, select=True,
                            states={'draft': [('readonly', False)]}, unique=True,
                            help='Name of the picking dispatch'),
        'date': fields.date('Date', required=True, readonly=True, select=True,
                            states={'draft': [('readonly', False)]},
                            help='date on which the picking dispatched is to be processed'),
        'picker_id': fields.many2one('res.users', 'Picker', readonly=True, required=True,
                            states={'draft': [('readonly', False)]}, select=True,
                            help='the user to which the pickings are assigned'),
        'move_ids': fields.one2many('stock.move', 'dispatch_id', 'Moves',
                                    states={'draft': [('readonly', False)]},
                                    readonly=True,
                                    help='the list of moves to be processed'),
        'backorder_id': fields.many2one('picking.dispatch', 'Back Order of',
                                        help='if this dispatch was split, this links to the dispatch order containing the other part which was processed',
                                        select=True),
        'state': fields.selection([('draft', 'Draft'),
                                   ('assigned', 'Assigned'),
                                   ('progress', 'In Progress'),
                                   ('done', 'Done'),
                                   ('cancel', 'Cancelled'),
                                   ], 'Dispatch State', readonly=True, select=True,
                                  help='the state of the picking. Workflow is draft -> assigned -> progress -> done or cancel'),
        'related_picking_ids': fields.function(_get_related_picking, method=True, type='one2many',
             relation='stock.picking', string='Related Dispatch Picking'),
        }

    _defaults = {
        'name': lambda obj, cr, uid, ctxt: obj.pool.get('ir.sequence').get(cr, uid, 'picking.dispatch'),
        'date': fields.date.context_today,
        'state': 'draft'
        }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        if 'name' not in default:
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'picking.dispatch')
        default['move_ids'] =  []
        default['related_picking_ids'] =  []
        res = super(PickingDispatch, self).copy(cr, uid, id, default, context)
        return res

    def action_assign(self, cr, uid, ids, context=None):
        _logger.debug('set state to assigned for picking.dispatch %s', ids)
        self.write(cr, uid, ids, {'state': 'assigned'}, context)
        return True

    def action_progress(self, cr, uid, ids, context=None):
        self.assert_start_ok(cr, uid, ids, context)
        _logger.debug('set state to progress for picking.dispatch %s', ids)
        self.write(cr, uid, ids, {'state': 'progress'}, context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(cr, uid, [('dispatch_id', 'in', ids)], context=context)
        return move_obj.action_partial_move(cr, uid, move_ids, context)

    def action_cancel(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(cr, uid, [('dispatch_id', 'in', ids)], context=context)
        res = move_obj.action_cancel(cr, uid, move_ids, context)
        # If dispatch is empty, we still need to cancel it !
        if not move_ids:
            _logger.debug('set state to cancel for picking.dispatch %s', ids)
            self.write(cr, uid, ids, {'state': 'cancel'}, context)
        return res

    def assert_start_ok(self, cr, uid, ids, context=None):
        now = datetime.now().date()
        for obj in self.browse(cr, uid, ids, context):
            date = datetime.strptime(obj.date, '%Y-%m-%d').date()
            if date < now:
                raise except_osv(_('Error'),
                                 _('This dispatch cannot be processed until %s') % obj.date)


class StockMove(Model):
    _inherit = 'stock.move'
    _columns = {'dispatch_id': fields.many2one('picking.dispatch', 'Dispatch',
                                               help='who this move is dispatched to'),
                }

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
        # * newly created moves (the processed part of partially processed moves) belonging
        #   to the same dispatch as the original move
        # so the difference between the original set of moves and the complete_moves is the
        # set of unprocessed moves
        unprocessed_move_ids = set(ids) - set(complete_move_ids)
        # unprocessed moves are still linked to the dispatch : this dispatch must not be marked as Done
        unfinished_dispatch_ids = {}
        for move in move_obj.browse(cr, uid, list(unprocessed_move_ids), context=context):
            if not move.dispatch_id:
                continue
            unfinished_dispatch_ids[move.dispatch_id.id] = None # value will be set later to a new dispatch
        finished_dispatches = {}
        for move in move_obj.browse(cr, uid, complete_move_ids, context=context):
            if not move.dispatch_id:
                continue
            dispatch_id = move.dispatch_id.id
            if dispatch_id in unfinished_dispatch_ids:
                # the dispatch was partially processed: we need to link the move to
                # a new dispatch containing only fully processed moves
                if unfinished_dispatch_ids[dispatch_id] is None:
                    # create a new dispatch, and record its id
                    _logger.debug('create backorder picking.dispatch of %s', dispatch_id)
                    new_dispatch_id = dispatch_obj.copy(cr, uid, dispatch_id,
                                                     {'backorder_id': dispatch_id,
                                                      })
                    unfinished_dispatch_ids[dispatch_id] = new_dispatch_id
                dispatch_id = unfinished_dispatch_ids[dispatch_id]
            finished_dispatches.setdefault(dispatch_id, []).append(move.id)
        for dispatch_id, move_ids in finished_dispatches.iteritems():
            move_obj.write(cr, uid, move_ids, {'dispatch_id': dispatch_id})
        if finished_dispatches:
            _logger.debug('set state to done for picking.dispatch %s', list(finished_dispatches))
            dispatch_obj.write(cr, uid, list(finished_dispatches),  {'state': 'done'}, context)
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
        move_obj = self.pool.get('stock.move')
        dispatch_obj = self.pool.get('picking.dispatch')
        dispatches = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.dispatch_id:
                dispatches.add(move.dispatch_id.id)
        for dispatch in dispatch_obj.browse(cr, uid, list(dispatches), context=context):
            if any(move.state!='cancel' for move in dispatch.move_ids):
                dispatches.remove(dispatch.id)
        if dispatches:
            _logger.debug('set state to cancel for picking.dispatch %s', list(dispatches))
            dispatch_obj.write(cr, uid, list(dispatches), {'state': 'cancel'}, context)
        return status

    def action_done(self, cr, uid, ids, context=None):
        """
        in addition to the parent method does, set the dispatch done if all moves are done or cancelled
        """
        _logger.debug('done stock.moves %s', ids)
        status = super(StockMove, self).action_done(cr, uid, ids, context)
        if not ids:
            return True
        move_obj = self.pool.get('stock.move')
        dispatch_obj = self.pool.get('picking.dispatch')
        dispatches = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.dispatch_id:
                dispatches.add(move.dispatch_id.id)
        for dispatch in dispatch_obj.browse(cr, uid, list(dispatches), context=context):
            if any(move.state not in ('cancel', 'done') for move in dispatch.move_ids):
                dispatches.remove(dispatch.id)
        if dispatches:
            _logger.debug('set state to done for picking.dispatch %s', list(dispatches))
            dispatch_obj.write(cr, uid, list(dispatches), {'state': 'done'}, context)
        return status


class StockPicking(Model):
    _inherit = "stock.picking"

    def _get_related_dispatch(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        if not ids:
            return result
        for pick_id in ids:
            result[pick_id] = []
        sql = ("SELECT DISTINCT sm.picking_id, sm.dispatch_id FROM stock_move sm "
              "WHERE sm.picking_id in %s AND sm.dispatch_id is NOT NULL")
        cr.execute(sql, (tuple(ids),))
        res = cr.fetchall()
        for picking_id, dispatch_id in res:
            result[picking_id].append(dispatch_id)
        return result

    _columns = {
        'related_dispatch_ids': fields.function(_get_related_dispatch, method=True, type='one2many',
            relation='picking.dispatch', string='Related Dispatch Picking'),
    }


class Product(Model):
    _inherit = "product.product"

    _columns = {
        'description_warehouse': fields.text('Warehouse Description', translate=True),
        }



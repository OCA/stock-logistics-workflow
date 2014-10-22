# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012-2014 Camptocamp SA
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
from openerp.osv import orm, fields
from openerp.osv.osv import except_osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class PickingDispatch(orm.Model):

    """New object that contain stock moves selected from stock.picking by the
    warehouse manager so that the warehouseman can go and bring the product
    where they're asked for.  The purpose is to know who will look for what in
    the warehouse. We don't use the stock.picking object cause we don't want to
    break the relation with the SO and all related workflow.

    This object is designed for the warehouse problematics and must help the
    people there to organize their work."""

    _name = 'picking.dispatch'
    _description = "Dispatch Picking Order"

    def _get_related_picking(self, cr, uid, ids, field_names, arg=None,
                             context=None):
        result = {}
        if not ids:
            return result
        for dispatch_id in ids:
            result[dispatch_id] = []
        sql = ("SELECT DISTINCT sm.dispatch_id, sm.picking_id "
               "FROM stock_move sm "
               "WHERE sm.dispatch_id in %s AND sm.picking_id is NOT NULL")
        cr.execute(sql, (tuple(ids),))
        res = cr.fetchall()
        for line in res:
            result[line[0]].append(line[1])
        return result

    _columns = {
        'name': fields.char(
            'Name', size=96, required=True, select=True,
            states={'draft': [('readonly', False)]}, unique=True,
            help='Name of the picking dispatch'),
        'date': fields.date(
            'Date', required=True, readonly=True, select=True,
            states={'draft': [('readonly', False)],
                    'assigned': [('readonly', False)]},
            help='date on which the picking dispatched is to be processed'),
        'picker_id': fields.many2one(
            'res.users', 'Picker', readonly=True,
            states={'draft': [('readonly', False)],
                    'assigned': [('readonly', False),
                                 ('required', True)]},
            select=True,
            help='the user to which the pickings are assigned'),
        'move_ids': fields.one2many('stock.move', 'dispatch_id', 'Moves',
                                    states={'draft': [('readonly', False)]},
                                    readonly=True,
                                    help='the list of moves to be processed'),
        'notes': fields.text('Notes', help='free form remarks'),
        'backorder_id': fields.many2one(
            'picking.dispatch', 'Back Order of',
            help='if this dispatch was split, this links to the dispatch '
            'order containing the other part which was processed',
            select=True),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('assigned', 'Assigned'),
                ('progress', 'In Progress'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
            ], 'Dispatch State', readonly=True, select=True,
            help='the state of the picking. '
            'Workflow is draft -> assigned -> progress -> done or cancel'),
        'related_picking_ids': fields.function(
            _get_related_picking, method=True, type='one2many',
            relation='stock.picking', string='Related Dispatch Picking'),
        'company_id': fields.many2one('res.company', 'Company',
                                      required=True),
    }

    def _default_company(self, cr, uid, context=None):
        company_obj = self.pool.get('res.company')
        return company_obj._company_default_get(cr, uid,
                                                'picking.dispatch',
                                                context=context)

    _defaults = {
        'name': lambda obj, cr, uid, ctxt: obj.pool.get('ir.sequence').get(
            cr, uid, 'picking.dispatch'),
        'date': fields.date.context_today,
        'state': 'draft',
        'company_id': _default_company,
    }

    def _check_picker_assigned(self, cr, uid, ids, context=None):
        for dispatch in self.browse(cr, uid, ids, context=context):
            if (dispatch.state in ('assigned', 'progress', 'done') and
                    not dispatch.picker_id):
                return False
        return True

    _constraints = [
        (_check_picker_assigned, 'Please select a picker.', ['picker_id'])
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        if 'name' not in default:
            default['name'] = self.pool.get(
                'ir.sequence').get(cr, uid, 'picking.dispatch')
        default['move_ids'] = []
        default['related_picking_ids'] = []
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
        if not ids:
            return True
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(
            cr, uid, [('dispatch_id', 'in', ids)], context=context)
        return move_obj.action_partial_move(cr, uid, move_ids, context)

    def check_finished(self, cr, uid, ids, context):
        """set the dispatch to finished if all the moves are finished"""
        if not ids:
            return True
        finished = []
        for dispatch in self.browse(cr, uid, ids, context=context):
            if all(
                move.state in ('cancel', 'done') for move in dispatch.move_ids
            ):
                finished.append(dispatch.id)
        _logger.debug('set state to done for picking.dispatch %s', finished)
        self.write(cr, uid, finished, {'state': 'done'}, context)
        return finished

    def action_cancel(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(
            cr, uid, [('dispatch_id', 'in', ids)], context=context)
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
            if now < date:
                raise except_osv(
                    _('Error'),
                    _('This dispatch cannot be processed until %s') % obj.date)

    def action_assign_moves(self, cr, uid, ids, context=None):
        move_obj = self.pool['stock.move']
        move_ids = move_obj.search(cr, uid,
                                   [('dispatch_id', 'in', ids)],
                                   context=context)
        move_obj.action_assign(cr, uid, move_ids)
        return True

    def check_assign_all(self, cr, uid, ids=None, domain=None, context=None):
        """ Try to assign moves of a selection of dispatches

        Called from a cron
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        if ids is None:
            if domain is None:
                domain = [('state', 'in', ('draft', 'assigned'))]
            ids = self.search(cr, uid, domain, context=context)
        self.action_assign_moves(cr, uid, ids, context=context)
        return True

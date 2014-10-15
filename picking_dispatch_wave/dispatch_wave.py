# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Romain Deheele
#    Copyright 2014 Camptocamp SA
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
#############################################################################
import logging

from openerp.osv import orm, fields
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class StockPickingDispatchWave(orm.TransientModel):
    _name = "stock.picking.dispatch.wave"

    def _get_pickings_to_do(self, cr, uid, max_nb, context=None):
        context = context or {}
        move_obj = self.pool['stock.move']
        move_ids = []
        picking_ids = set()
        move_ids = move_obj.search(cr, uid,
                                   [('dispatch_id', '=', False),
                                    ('state', '=', 'assigned'),
                                    ('type', '=', 'out'),
                                    ('location_id.usage', '=', 'internal')],
                                   order='date_expected DESC',
                                   context=context)
        for move in move_obj.browse(cr, uid, move_ids, context=context):
            if len(picking_ids) == max_nb:
                break
            if move.picking_id.state == 'assigned' and \
                    move.picking_id.id not in picking_ids:
                picking_ids.add(move.picking_id.id)
        return list(picking_ids)

    def _get_moves_from_picking_list(self, cr, uid, picking_ids, context=None):
        context = context or {}
        move_obj = self.pool['stock.move']
        move_ids = move_obj.search(cr, uid,
                                   [('picking_id', 'in', picking_ids)],
                                   context=context)
        return move_ids

    def _get_moves_from_pickings_to_do(self, cr, uid, max_nb, context=None):
        context = context or {}
        move_ids = []
        picking_ids = self.\
            _get_pickings_to_do(cr, uid, max_nb, context=context)
        if picking_ids:
            move_ids = self._get_moves_from_picking_list(cr, uid, picking_ids,
                                                         context=context)
        return move_ids

    _columns = {
        'max_pickings_to_do': fields.integer('Number maximum of pickings '
                                             'to prepare',
                                             help='number maximum of pickings '
                                             'that we want to prepare'),
        'picker_id': fields.many2one('res.users', 'User', required=True,
                                     help='the user to which the pickings '
                                     'are assigned'),
    }

    _defaults = {
        'max_pickings_to_do': 0,
        'picker_id': lambda self, cr, uid, ctx: uid,
    }

    def action_create_picking_dispatch(self, cr, uid, ids, context=None):
        context = context or {}
        wave = self.browse(cr, uid, ids, context=context)[0]
        if wave.max_pickings_to_do:
            move_ids = self.\
                _get_moves_from_pickings_to_do(cr, uid,
                                               wave.max_pickings_to_do,
                                               context=context)
            if move_ids:
                # create picking_dispatch
                dispatch_obj = self.pool['picking.dispatch']
                dispatch_vals = {
                    'picker_id': wave.picker_id.id
                }
                dispatch_id = dispatch_obj.create(cr, uid,
                                                  dispatch_vals,
                                                  context=context)
                # affect move_ids on the new dispatch
                self.pool['stock.move'].write(cr, uid, move_ids,
                                              {'dispatch_id': dispatch_id},
                                              context=context)
                # picking dispatch can be directly assigned
                dispatch_obj.action_assign(cr, uid, [dispatch_id],
                                           context=context)
                context['active_id'] = dispatch_id
                return {
                    'domain': str([('id', '=', dispatch_id)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'picking.dispatch',
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'res_id': dispatch_id,
                }
            else:
                raise orm.except_orm(_('Information'),
                                     _('No ready pickings to deliver!'))
        else:
            raise orm.except_orm(_('Error'),
                                 _('You need to set at least one unit to do.'))

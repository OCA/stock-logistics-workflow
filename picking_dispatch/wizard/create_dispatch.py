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
from openerp.osv.orm import TransientModel
from openerp.osv import osv, fields
from openerp.tools.translate import _


class picking_dispatch_creator(TransientModel):
    """Create a picking dispatch from stock.picking. This will take all related
    stock move from the selected picking and put them in the dispatch order."""

    _name = 'picking.dispatch.creator'
    _description = 'Picking Dispatch Creator'
    _columns = {
        'name': fields.char('Name', size=96, required=True,
                           help='Name of the picking dispatch'),
        'date': fields.date('Date', required=True, select=True,
                            help='Date on which the picking dispatched is to be processed'),
        'picker_id': fields.many2one('res.users', 'Picker', required=True,
                                     help='The user to which the pickings are assigned'),
        'notes': fields.text('Notes', help='free form remarks'),
        }

    def _default_picker(self, cr, uid, context=None):
        user_obj = self.pool.get('res.users')
        company = user_obj.browse(cr, uid, uid).company_id
        return company.default_picker_id.id if company.default_picker_id else False

    _defaults = {
        'name': lambda obj, cr, uid, ctxt: obj.pool.get('ir.sequence').get(cr, uid, 'picking.dispatch'),
        'date': fields.date.context_today,
        'picker_id': _default_picker,
        }
    def action_create_dispatch(self, cr, uid, ids, context=None):
        """
        Open the historical margin view
        """
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        dispatch_obj = self.pool.get('picking.dispatch')
        if context is None:
            context = {}
        wiz = self.read(cr, uid, ids, [], context=context)[0]
        ctx = context.copy()
        all_move_ids = move_obj.search(cr, uid,
                               [('picking_id', 'in', context['active_ids'])],
                               context=context)
        ok_move_ids = []
        already_dispatched_ids = {}
        wrong_state_ids = {}
        for move in move_obj.browse(cr, uid, all_move_ids, context=context):
            if move.dispatch_id:
                already_dispatched_ids.setdefault(move.dispatch_id.name, []).append((move.id, move.picking_id.name))
            elif move.state not in ('confirmed', 'waiting', 'assigned'):
                wrong_state_ids.setdefault(move.picking_id.name, {}).setdefault(move.state, []).append(move.id)
            else:
                ok_move_ids.append(move.id)
        if not ok_move_ids:
            problems = [_("No valid stock moves found to create the dispatch!"),
                        _("(Only move that are not part of a dispatch order and in "
                          "confirm, waiting or assigned state can be used)")]
            for dispatch_name, mvs in already_dispatched_ids.iteritems():
                mvs.sort()

                problems.append(_('Dispatch %s already covers moves %s') % \
                                (dispatch_name,
                                 u', '.join(['%s [%s]' % (mv, pck) for mv, pck in mvs]))
                                )
            for pck, states in wrong_state_ids.iteritems():
                for state, mvs in states.iteritems():
                    problems.append(_('Moves %s from picking %s are in state %s') % \
                                    (tuple(mvs), pck, state))
            raise osv.except_osv(_('Warning !'), u'\n'.join(problems))

        data = {'date': wiz.get('date'),
                'name': wiz.get('name'),
                'notes': wiz.get('notes'),
                }
        if wiz.get('picker_id'):
            data['picker_id'] = wiz.get('picker_id')[0]
        dispatch_id = dispatch_obj.create(cr, uid, data, context=context)
        # for move_id in move_ids:
        move_obj.write(cr, uid, ok_move_ids, {'dispatch_id': dispatch_id}, context=context)

        return {'type': 'ir.actions.act_window_close'}

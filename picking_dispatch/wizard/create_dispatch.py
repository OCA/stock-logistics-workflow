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
        'date': fields.date('Date', required=True, select=True,
                            help='Date on which the picking dispatched is to be processed'),
        'picker_id': fields.many2one('res.users', 'Picker',
                                     help='The user to which the pickings are assigned'),
        }

    _defaults = {
        'date': fields.date.context_today,
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
        move_ids = move_obj.search(cr, uid,
                               [('picking_id', 'in', context['active_ids']),
                                ('dispatch_id', '=', False),
                                ('state', 'in', ('confirmed', 'waiting', 'assigned'))],
                               context=context)
        if not move_ids:
            raise osv.except_osv(_('Warning !'), _("No valide stock moves found to create the dispatch ! "
                "(Only move that are not part of a disptach order and in confirm, waiting or assigned state can be "
                "used)"))
        data = {'date': wiz.get('date'),
                }
        if wiz.get('picker_id'):
            data['picker_id'] = wiz.get('picker_id')[0]
        dispatch_id = dispatch_obj.create(cr, uid, data, context=context)
        # for move_id in move_ids:
        move_obj.write(cr, uid, move_ids, {'dispatch_id': dispatch_id}, context=context)

        return {'type': 'ir.actions.act_window_close'}
        # XXX display moves
        ## data_pool = self.pool.get('ir.model.data')
        ## filter_ids = data_pool.get_object_reference(cr, uid, 'product',
        ##                                             'product_search_form_view')
        ## product_view_id = data_pool.get_object_reference(cr, uid,
        ##                                                  'product_historical_margin',
        ##                                                  'view_product_historical_margin')
        ## if filter_ids:
        ##     filter_id = filter_ids[1]
        ## else:
        ##     filter_id = 0
        ## return {
        ##     'type': 'ir.actions.act_window',
        ##     'name': _('Historical Margins'),
        ##     'context': ctx,
        ##     'view_type': 'form',
        ##     'view_mode': 'tree',
        ##     'res_model': 'product.product',
        ##     'view_id': product_view_id[1],
        ##     'search_view_id': filter_id,
        ##     }

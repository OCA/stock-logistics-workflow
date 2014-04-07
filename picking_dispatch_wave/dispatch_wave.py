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

    def _get_moves_from_oldest_sales(self, cr, uid, nb_sales, context=None):
        context = context or {}
        move_ids = []
        # get n order sales that have an assigned picking
        sql = """ SELECT so.id FROM sale_order AS so
        LEFT JOIN stock_picking AS pick ON pick.sale_id = so.id
        WHERE pick.state = 'assigned' and pick.type = 'out'
        ORDER BY so.date_order ASC
        LIMIT %d
        """
        cr.execute(sql % nb_sales)
        oldest_sales = cr.fetchall()
        # get pickings from oldest sales
        picking_obj = self.pool['stock.picking']
        picking_ids = picking_obj.search(cr, uid,
                                         [('sale_id', 'in', oldest_sales),
                                          ('type', '=', 'out')],
                                         context=context)
        if picking_ids:
            # get moves from pickings
            move_obj = self.pool['stock.move']
            move_ids = move_obj.search(cr, uid,
                                       [('picking_id', 'in', picking_ids)],
                                       context=context)
        return move_ids

    _columns = {
        'nb_sales': fields.integer('How many sales?'),
        }
    _defaults = {
        'nb_sales': 0,
        }

    def action_create_picking_dispatch(self, cr, uid, ids, context=None):
        context = context or {}
        nb_sales = self.browse(cr, uid, ids, context=context)[0]['nb_sales']
        if nb_sales:
            move_ids = self._get_moves_from_oldest_sales(cr, uid, nb_sales,
                                                         context=context)
            if move_ids:
                # create picking_dispatch
                dispatch_obj = self.pool['picking.dispatch']
                dispatch_id = dispatch_obj.create(cr, uid, {}, context=context)
                # affect move_ids on the new dispatch
                self.pool['stock.move'].write(cr, uid, move_ids,
                                              {'dispatch_id': dispatch_id},
                                              context=context)
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
                                 _('You need to set at least one sale order.'))

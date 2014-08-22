# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
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
##############################################################################

from openerp.osv import orm


class StockPickingOut(orm.Model):

    _inherit = 'stock.picking.out'

    def compute_mts_delivery_dates(self, cr, uid, product_id, context=None):
        # TODO: use only mts moves /products
        move_obj = self.pool['stock.move']
        product_obj = self.pool['product.product']
        user_obj = self.pool['res.users']

        remaining_stock = product.qty_available
        product = product_obj.browse(cr, uid, product_id, context=context)
        security_days = user_obj.browse(
            cr, uid, uid, context=context
        ).company_id.security_lead

        move_out_ids = move_obj.search(cr, uid, [
            ('product_id', '=', product_id),
            ('picking_id.type', '=', 'in'),
            ('state', 'in', ('confirmed', 'assigned', 'pending')),
        ], order='date_expected', context=context)

        move_in_ids = move_obj.search(cr, uid, [
            ('product_id', '=', product_id),
            ('picking_id.type', '=', 'in'),
            ('state', 'in', ('confirmed', 'assigned', 'pending')),
        ], order='date_expected', context=context)
        moves_in_iter = iter(move_obj.browse(cr, uid, move_in_ids, 
                                             context=context))

        for move_out in move_obj.browse(cr, uid, move_out_ids, 
                                        context=context):
            import pdb; pdb.set_trace()  # XXX BREAKPOINT
            if remaining_stock:
                if remaining_stock >= move_out.product_qty:
                   remaining_stock -= move_out.product_qty
                   move_obj.write(cr, uid, move_out.id, {
                       'date_expected': today + security_days,
                   }, context=context)
                else:
                    remaining_stock = 0.0


        return True


    def compute_all_mts_delivery_dates(self, cr, uid, context=None):
        # TODO: use only mts moves /products
        move_obj = self.pool['stock.move']

        moves_out_grouped = move_obj.read_group(
            cr,
            uid,
            domain=[
                ('picking_id.type', '=', 'in'),
                ('state', 'in', ('confirmed', 'assigned', 'pending'))
            ],
            fields=['product_id'],
            groupby=['product_id'],
            context=context,
        )

        product_ids = [g['product_id'][0] for g in moves_out_grouped]

        for product_id in product_ids:
            self.compute_mts_delivery_dates(cr, uid, product_id,
                                            context=context)

        return True

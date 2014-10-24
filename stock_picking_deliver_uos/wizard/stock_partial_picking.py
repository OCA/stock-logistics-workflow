# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
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

from osv import fields, orm
import openerp.addons.decimal_precision as dp


class Stock_Partial_Picking_Line(orm.TransientModel):
    _inherit = 'stock.partial.picking.line'

    def on_change_product_uos_qty(
            self, cr, uid, ids,
            product_uos_qty, move_id, context=None):
        result = {}
        move_obj = self.pool[('stock.move')].browse(
            cr, uid, move_id, context=context)
        result['value'] = {'quantity': move_obj.product_qty*(
            product_uos_qty/move_obj.product_uos_qty)}
        return result

    _columns = {
        'product_uos': fields.many2one('product.uom', 'Product UOS'),
        'product_uos_qty': fields.float(
            'Quantity (UOS)',
            digits_compute=dp.get_precision('Product Unit of Measure')),
    }


class stock_partial_picking(orm.TransientModel):
    _inherit = 'stock.partial.picking'

    def _partial_move_for(self, cr, uid, move, context=None):
        partial_move = super(
            stock_partial_picking,
            self)._partial_move_for(cr, uid, move)
        partial_move.update({
            'product_uos': move.product_uos.id,
            'product_uos_qty': move.product_uos_qty
        })
        return partial_move

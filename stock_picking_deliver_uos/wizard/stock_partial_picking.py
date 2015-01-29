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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class StockPartialPickingLine(orm.TransientModel):
    _inherit = 'stock.partial.picking.line'

    def on_change_product_uos_qty(
            self, cr, uid, ids,
            product_uos_qty, move_id, context=None):
        result = {}
        move_obj = self.pool['stock.move'].browse(
            cr, uid, move_id, context=context)
        result['value'] = {'quantity': move_obj.product_qty*(
            product_uos_qty/move_obj.product_uos_qty)}
        return result

    _columns = {
        'product_uos': fields.related(
            'move_id', 'product_uos',
            type="many2one", relation="product.uom", string='Product UOS',
            readonly=True),
        'product_uos_qty': fields.float(
            'Quantity (UOS)',
            digits_compute=dp.get_precision('Product Unit of Measure')),
    }


class StockPartialPicking(orm.TransientModel):
    _inherit = 'stock.partial.picking'

    def _partial_move_for(self, cr, uid, move, context=None):
        partial_move = super(
            StockPartialPicking,
            self)._partial_move_for(cr, uid, move)
        partial_move.update({
            'product_uos': move.product_uos.id,
            'product_uos_qty': move.product_uos_qty
        })
        return partial_move

    def do_partial(self, cr, uid, ids, context=None):
        res = super(StockPartialPicking, self).do_partial(
            cr, uid, ids, context=context)
        if (
            res.get('res_id') and res.get('context')
            and res['context'].get('active_id')
        ):
            wizard = self.browse(cr, uid, ids[0], context=context)
            picking_pool = self.pool['stock.picking']
            delivered_picking_id = res['res_id']
            delivered_picking = picking_pool.browse(
                cr, uid, delivered_picking_id, context=context)
            for delivered_line in delivered_picking.move_lines:
                for wizard_line in wizard.move_ids:
                    if (
                        wizard_line.product_id.id
                        == delivered_line.product_id.id
                        and
                        wizard_line.quantity == delivered_line.product_qty
                        and
                        wizard_line.product_uom.id
                        == delivered_line.product_uom.id
                    ):
                        delivered_line.write(
                            {'product_uos_qty': wizard_line.product_uos_qty},
                            context=context)
                        wizard_line.move_id.write(
                            {'product_uos_qty': wizard_line.product_uos_qty * (
                                wizard_line.move_id.product_qty
                                / delivered_line.product_qty)},
                            context=context)
                        break
        return res

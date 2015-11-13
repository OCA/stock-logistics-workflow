# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class AccountInvoice(orm.Model):

    _inherit = 'account.invoice'

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            for line in invoice.invoice_line:
                move_obj = self.pool['stock.move']
                picking_obj = self.pool['stock.picking']
                cr.execute("""
                SELECT move_id
                FROM stock_move_invoice_rel
                WHERE invoice_line_id = %s
                """, (line.id, ))
                res = cr.fetchone()
                if res:
                    move_id = res[0]
                    move = move_obj.browse(cr, uid, move_id, context=context)
                    if move.picking_id and move.picking_id.state != \
                            '2binvoiced':
                        picking_obj.write(cr, uid,  [move.picking_id.id],
                                          {'invoice_state': '2binvoiced'},
                                          context=context)
        return super(AccountInvoice, self).unlink(cr, uid, ids,
                                                  context=context)


class AccountInvoiceLine(orm.Model):

    _inherit = 'account.invoice.line'

    _columns = {
        'stock_moves': fields.many2many('stock.move', 'stock_move_invoice_rel',
                                        'invoice_line_id', 'move_id',
                                        'Stock Moves', readonly=True)
    }

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if 'stock_invoice_onshipping' in context:
                continue
            move_obj = self.pool['stock.move']
            picking_obj = self.pool['stock.picking']
            cr.execute("""
            SELECT move_id
            FROM stock_move_invoice_rel
            WHERE invoice_line_id = %s
            """, (line.id, ))
            res = cr.fetchone()
            if res:
                move_id = res[0]
                move = move_obj.browse(cr, uid, move_id, context=context)
                if move.picking_id and move.picking_id.state != '2binvoiced':
                    picking_obj.write(cr, uid,  [move.picking_id.id],
                                      {'invoice_state': '2binvoiced'},
                                      context=context)
        return super(AccountInvoiceLine, self).unlink(cr, uid, ids,
                                                      context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if not isinstance(ids, list):
            ids = [ids]
        res = super(AccountInvoiceLine, self).write(cr, uid, ids, vals,
                                                    context=context)
        if 'quantity' in vals:
            for line in self.browse(cr, uid, ids, context=context):
                picking_obj = self.pool['stock.picking']
                for move in line.stock_moves:
                    product_qty = move.product_uos_qty or move.product_qty
                    if move.picking_id:
                        if move.invoiced_qty > product_qty:
                            raise orm.except_orm(
                                'Error!',
                                'You are trying to invoice more quantity '
                                'than what has actually been received or '
                                'delivered.')
                        if move.invoiced_qty != product_qty:
                            invoice_state = '2binvoiced'
                        else:
                            invoice_state = 'invoiced'
                        picking_obj.write(cr, uid, [move.picking_id.id],
                                          {'invoice_state': invoice_state},
                                          context=context)
        return res

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
        inv_line_obj = self.pool['account.invoice.line']
        for invoice in self.browse(cr, uid, ids, context=context):
            line_ids = [line.id for line in invoice.invoice_line]
            inv_line_obj.update_stock_moves(cr, uid, line_ids,
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

    def update_stock_moves(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if 'stock_invoice_onshipping' in context:
                continue
            picking_obj = self.pool['stock.picking']
            for move in line.stock_moves:
                if move.picking_id and move.picking_id.state != '2binvoiced':
                    picking_obj.write(cr, uid,  [move.picking_id.id],
                                      {'invoice_state': '2binvoiced'},
                                      context=context)

    def unlink(self, cr, uid, ids, context=None):
        self.update_stock_moves(cr, uid, ids, context=context)
        return super(AccountInvoiceLine, self).unlink(cr, uid, ids,
                                                      context=context)

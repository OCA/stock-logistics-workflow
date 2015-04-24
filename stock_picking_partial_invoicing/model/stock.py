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

from openerp.osv import fields, orm


class stock_move(orm.Model):

    def _invoiced_qty(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for move in self.browse(cursor, user, ids, context=context):
            invoiced_qty = 0.0
            for invoice_line in move.invoice_lines:
                invoiced_qty += invoice_line.quantity
            res[move.id] = invoiced_qty
        return res

    _inherit = 'stock.move'

    _columns = {
        'invoiced_qty': fields.function(_invoiced_qty,
                                        string='Invoiced quantity',
                                        type='float'),
        'invoice_lines': fields.many2many('account.invoice.line',
                                          'stock_move_invoice_rel',
                                          'move_id', 'invoice_line_id',
                                          'Invoice Lines', readonly=True),
    }


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        res = super(stock_picking, self)._invoice_line_hook(
            cr, uid, move_line, invoice_line_id)
        move_line.write({'invoice_lines': [(4, invoice_line_id)]})
        return res
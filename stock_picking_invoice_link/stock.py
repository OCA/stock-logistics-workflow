# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
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


class StockMove(orm.Model):
    _inherit = "stock.move"

    _columns = {
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Invoice line', readonly=True),
    }


class StockPicking(orm.Model):
    _inherit = "stock.picking"

    def _get_invoice_view_xmlid(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.invoice_id:
                if pick.invoice_id.type in ('in_invoice', 'in_refund'):
                    res[pick.id] = 'account.invoice_supplier_form'
                else:
                    res[pick.id] = 'account.invoice_form'
            else:
                res[pick.id] = False
        return res

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Invoice', readonly=True),
        'invoice_view_xmlid': fields.function(
            _get_invoice_view_xmlid, type='char', string="Invoice View XMLID",
            readonly=True),
    }

    def action_invoice_create(
            self, cr, uid, ids, journal_id, group=False,
            type='out_invoice', context=None
    ):
        res = super(StockPicking, self).action_invoice_create(
            cr, uid, ids, journal_id, group=group,
            type='out_invoice', context=context)
        self.write(cr, uid, ids[0], {'invoice_id': res[0]})
        return res

    def _invoice_create_line(
            self, cr, uid, moves, journal_id,
            inv_type='out_invoice', context=None
    ):
        res = super(StockPicking, self)._invoice_create_line(
            cr, uid, moves, journal_id,
            inv_type='out_invoice', context=context)
        stock_move_obj = self.pool.get('stock.move')
        for move in moves:
            stock_move_obj.write(
                cr, uid, [move.id], {'invoice_line_id':  res[0]})
        return res


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'picking_ids': fields.one2many(
            'stock.picking', 'invoice_id', 'Related Pickings', readonly=True,
            help="Related pickings (only when the invoice has been generated "
                 "from the picking)."),
    }


class AccountInvoiceLine(orm.Model):
    _inherit = "account.invoice.line"

    _columns = {
        'move_line_ids': fields.one2many(
            'stock.move', 'invoice_line_id', 'Related Stock Moves',
            readonly=True,
            help="Related stock moves (only when the invoice has been "
                 "generated from the picking)."),
    }

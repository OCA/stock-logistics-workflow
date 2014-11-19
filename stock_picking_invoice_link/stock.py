# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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
    _inherit = "stock.move"

    _columns = {
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Invoice Line', readonly=True),
    }

    def _create_invoice_line_from_vals(
            self, cr, uid, move, invoice_line_vals, context=None):
        inv_line_id = super(stock_move, self)._create_invoice_line_from_vals(
            cr, uid, move, invoice_line_vals, context=context)
        move.write({'invoice_line_id': inv_line_id})
        return inv_line_id


class stock_picking(orm.Model):
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

    def _create_invoice_from_picking(
            self, cr, uid, picking, vals, context=None):
        invoice_id = super(stock_picking, self)._create_invoice_from_picking(
            cr, uid, picking, vals, context=context)
        picking.write({'invoice_id': invoice_id})
        return invoice_id


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'picking_ids': fields.one2many(
            'stock.picking', 'invoice_id', 'Related Pickings', readonly=True,
            help="Related pickings "
            "(only when the invoice has been generated from the picking)."),
    }


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    _columns = {
        'move_line_ids': fields.one2many(
            'stock.move', 'invoice_line_id', 'Related Stock Moves',
            readonly=True,
            help="Related stock moves "
            "(only when the invoice has been generated from the picking)."),
    }

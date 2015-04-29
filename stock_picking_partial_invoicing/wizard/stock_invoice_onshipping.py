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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class StockInvoiceOnshipping(orm.TransientModel):

    _inherit = 'stock.invoice.onshipping'

    _columns = {
        'line_ids': fields.one2many('stock.invoice.onshipping.line',
                                    'wizard_id', 'Lines'),
    }

    def default_get(self, cr, uid, fields, context=None):
        picking_obj = self.pool.get('stock.picking')
        lines = []
        for picking in picking_obj.browse(cr, uid,
                                          context.get('active_ids', []),
                                          context=context):
            for move in picking.move_lines:
                product_qty = move.product_uos_qty or move.product_qty
                qty_to_invoice = product_qty - move.invoiced_qty
                if qty_to_invoice != 0.0:
                    lines.append({
                        'picking_id': move.picking_id.id,
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_qty': qty_to_invoice,
                        'invoiced_qty': qty_to_invoice,
                        'price_unit': move.price_unit,
                    })
        defaults = super(StockInvoiceOnshipping, self).default_get(
            cr, uid, fields, context=context)
        defaults['line_ids'] = lines
        return defaults

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_obj = self.pool['stock.picking']
        invoice_obj = self.pool['account.invoice']
        invoice_line_obj = self.pool['account.invoice.line']
        wizard = self.browse(cr, uid, ids[0], context=context)
        changed_lines = {}
        for line in wizard.line_ids:
            if line.invoiced_qty > line.product_qty:
                raise orm.except_orm(
                    _('Error'),
                    _("""Quantity to invoice is greater
                    than available quantity""")
                )
            if line.invoiced_qty == 0.0:
                continue
            if line.picking_id.id not in changed_lines:
                changed_lines[line.picking_id.id] = {}
            changed_lines[line.picking_id.id][line.move_id.id] = {
                'product_qty': line.move_id.product_qty,
                'invoiced_qty': line.invoiced_qty,
            }
        if not changed_lines:
            raise orm.except_orm(
                _('Error'),
                _("""Nothing to invoice!""")
            )
        res = super(StockInvoiceOnshipping, self).create_invoice(
            cr, uid, ids, context=context)
        invl_to_rm = []
        invl_qty_to_upd = {}
        for picking in picking_obj.browse(cr, uid, res.keys(),
                                          context=context):
            if not res[picking.id]:
                continue
            new_invoice = invoice_obj.browse(cr, uid, res[picking.id],
                                             context=context)
            for move in picking.move_lines:
                if move.id not in changed_lines[picking.id].keys():
                    # If that stock move was not selected to be invoiced,
                    # Look for the new invoice's lines that were already
                    # associated to the stock move, and remove them.
                    for inv_line in move.invoice_lines:
                        if inv_line.invoice_id.id == new_invoice.id:
                            invl_to_rm.append(inv_line.id)
                else:
                    # If that stock move was selected to be invoiced,
                    # Look for the new invoice's lines that were already
                    # associated to the stock move, and update them.
                    for inv_line in move.invoice_lines:
                        if inv_line.invoice_id.id == new_invoice.id:
                            # Update the invoice line to the quantity that
                            # the user indicated to be invoiced for that
                            # stock move in the wizard.
                            invl_qty_to_upd[inv_line.id] = \
                                changed_lines[picking.id][move.id][
                                    'invoiced_qty']
        if invl_to_rm:
            invoice_line_obj.unlink(cr, uid, invl_to_rm, context=context)

        for inv_line in invl_qty_to_upd:
            invoice_line_obj.write(
                cr, uid, inv_line,
                {'quantity': invl_qty_to_upd[inv_line]}, context=context)
        for picking in picking_obj.browse(cr, uid, res.keys(),
                                          context=context):
            inv_type = picking_obj._get_invoice_type(picking)
            invoice_obj.button_compute(cr, uid, [res[picking.id]],
                                       context=context,
                                       set_total=(inv_type in ('in_invoice',
                                                               'in_refund')))
        for picking in picking_obj.browse(cr, uid, res.keys(),
                                          context=context):
            for move in picking.move_lines:
                product_qty = move.product_uos_qty or move.product_qty
                if move.invoiced_qty != product_qty:
                    picking_obj.write(cr, uid, [picking.id],
                                      {'invoice_state': '2binvoiced'},
                                      context=context)
        return res


class StockInvoiceOnshippingLine(orm.TransientModel):

    _name = 'stock.invoice.onshipping.line'

    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Stock Picking',
                                      readonly=True),
        'move_id': fields.many2one('stock.move', 'Stock move', readonly=True),
        'product_id': fields.related(
            'move_id', 'product_id', type='many2one',
            relation='product.product',
            string='Product', readonly=True),
        'product_qty': fields.float(
            'Quantity', digits_compute=dp.get_precision(
                'Product Unit of Measure'), readonly=True,
            help='Remaining quantity to invoice'),
        'price_unit': fields.related(
            'move_id', 'price_unit', type='float',
            string='Unit Price', readonly=True),
        'invoiced_qty': fields.float(
            'Quantity to invoice', digits_compute=dp.get_precision(
                'Product Unit of Measure')),
        'wizard_id': fields.many2one('stock.invoice.onshipping', 'Wizard'),
    }

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

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class StockInvoiceOnshippingLine(models.TransientModel):

    _name = 'stock.invoice.onshipping.line'
    _description = 'Invoice lines'

    picking_id = fields.Many2one('stock.picking', 'Stock Picking',
                                 readonly=True)
    move_id = fields.Many2one('stock.move', 'Stock move', readonly=True)
    product_id = fields.Many2one('product.product',
                                 string='Product',
                                 related='move_id.product_id', readonly=True)
    product_qty = fields.Float(
        'Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
        readonly=True, help='Remaining quantity to invoice')
    price_unit = fields.Float(
        string='Unit Price', related='move_id.price_unit', readonly=True)
    invoiced_qty = fields.Float(
        'Quantity to invoice',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    wizard_id = fields.Many2one('stock.invoice.onshipping', 'Wizard')


class StockInvoiceOnshipping(models.TransientModel):

    _inherit = 'stock.invoice.onshipping'

    line_ids = fields.One2many('stock.invoice.onshipping.line',
                               'wizard_id', 'Lines')

    @api.model
    def default_get(self, fields):
        picking_obj = self.env['stock.picking']
        lines = []
        active_ids = self.env.context.get('active_ids', [])
        for picking in picking_obj.browse(active_ids):
            for move in picking.move_lines:
                quantity = move.product_uom_qty
                if move.product_uos:
                    quantity = move.product_uos_qty
                qty_to_invoice = quantity - move.invoiced_qty
                if qty_to_invoice != 0.0:
                    lines.append({
                        'picking_id': move.picking_id.id,
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_qty': qty_to_invoice,
                        'invoiced_qty': qty_to_invoice,
                        'price_unit': move.price_unit,
                    })
        defaults = super(StockInvoiceOnshipping, self).default_get(fields)
        defaults['line_ids'] = lines
        return defaults

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        changed_lines = {}

        for line in self.line_ids:
            if not line.picking_id:
                raise exceptions.Warning(
                    _('Error'),
                    _("""You cannot add additional lines to invoice.""")
                )
            if line.invoiced_qty > line.product_qty:
                raise exceptions.Warning(
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
            raise exceptions.Warning(
                _('Error'),
                _("""Nothing to invoice!""")
            )
        res = super(StockInvoiceOnshipping, self).create_invoice()
        invl_to_rm = []
        invl_qty_to_upd = {}
        picking_ids = []
        for line in self.line_ids:
            picking_ids.append(line.picking_id.id)

        for picking in picking_obj.browse(picking_ids):
            for move in picking.move_lines:
                if move.id not in changed_lines[picking.id].keys():
                    # If that stock move was not selected to be invoiced,
                    # Look for the new invoice's lines that were already
                    # associated to the stock move, and remove them.
                    for inv_line in move.invoice_lines:
                        if inv_line.invoice_id.id in res:
                            invl_to_rm.append(inv_line.id)
                else:
                    # If that stock move was selected to be invoiced,
                    # Look for the new invoice's lines that were already
                    # associated to the stock move, and update them.
                    for inv_line in move.invoice_lines:
                        if inv_line.invoice_id.id in res:
                            # Update the invoice line to the quantity that
                            # the user indicated to be invoiced for that
                            # stock move in the wizard.
                            invl_qty_to_upd[inv_line.id] = \
                                changed_lines[picking.id][move.id][
                                    'invoiced_qty']
        invoice_line_obj.browse(invl_to_rm).unlink()
        inv_ids_to_update = []
        for inv_line in invoice_line_obj.browse(invl_qty_to_upd.keys()):
            inv_line.write({'quantity': invl_qty_to_upd[inv_line.id]})
            inv_ids_to_update.append(inv_line.invoice_id.id)
        journal2type = {'sale': 'out_invoice', 'purchase': 'in_invoice',
                        'sale_refund': 'out_refund',
                        'purchase_refund': 'in_refund'}
        inv_type = journal2type.get(self.journal_type) or 'out_invoice'
        invoices_to_update = invoice_obj.browse(inv_ids_to_update)
        invoices_to_update.button_compute(
            set_total=(inv_type in ('in_invoice', 'in_refund')))
        for picking in picking_obj.browse(picking_ids):
            for move in picking.move_lines:
                product_qty = move.product_uos_qty or move.product_qty
                if move.invoiced_qty != product_qty:
                    move.write({'invoice_state': '2binvoiced'})
        return res

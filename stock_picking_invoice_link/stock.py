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

from openerp import models, api, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    invoice_line_id = fields.Many2one(comodel_name='account.invoice.line',
                                      string='Invoice Line', readonly=True)

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        inv_line_id = super(StockMove, self)._create_invoice_line_from_vals(
            move, invoice_line_vals)
        move.invoice_line_id = inv_line_id
        move.picking_id.invoice_id = invoice_line_vals['invoice_id']
        return inv_line_id


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.one
    def _get_invoice_view_xmlid(self):
        if self.invoice_id:
            if self.invoice_id.type in ('in_invoice', 'in_refund'):
                self.invoice_view_xmlid = 'account.invoice_supplier_form'
            else:
                self.invoice_view_xmlid = 'account.invoice_form'

    invoice_id = fields.Many2one(comodel_name='account.invoice',
                                 string='Invoice', readonly=True)
    invoice_view_xmlid = fields.Char(compute='_get_invoice_view_xmlid',
                                     string="Invoice View XMLID",
                                     readonly=True)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_ids = fields.One2many(
        comodel_name='stock.picking', inverse_name='invoice_id',
        string='Related Pickings', readonly=True,
        copy=False,
        help="Related pickings "
        "(only when the invoice has been generated from the picking).")


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.One2many(
        comodel_name='stock.move', inverse_name='invoice_line_id',
        string='Related Stock Moves', readonly=True,
        help="Related stock moves "
        "(only when the invoice has been generated from the picking).")

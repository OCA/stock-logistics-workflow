# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2017 BCIM (<http://www.bcim.be>)
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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        res = super(SaleOrderLine, self).invoice_line_create(invoice_id, qty)
        self.mapped('procurement_ids') \
            .mapped('move_ids') \
            .filtered(
                lambda x: x.state == 'done' and
                not x.location_dest_id.scrap_location and
                x.location_dest_id.usage == 'customer') \
            .mapped('picking_id') \
            .write({'invoice_id': invoice_id})
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        # move_ids = self.procurement_ids.mapped('move_ids').filtered(
        #     lambda x: x.state == 'done' and
        #     not x.location_dest_id.scrap_location and
        #     x.location_dest_id.usage == 'customer').ids

        # For performance reason, we compute the list of move in SQL
        self._cr.execute("""
            SELECT stock_move.id FROM stock_move
            LEFT JOIN stock_location
                ON stock_location.id=stock_move.location_dest_id
            LEFT JOIN procurement_order
                ON procurement_order.id=stock_move.procurement_id
            LEFT JOIN sale_order_line
                ON sale_order_line.id=procurement_order.sale_line_id
            WHERE stock_move.state='done'
                AND stock_location.scrap_location != 't'
                AND stock_location.usage = 'customer'
                AND sale_order_line.id in %s
            """, (tuple(self.ids),))

        move_ids = [row[0] for row in self._cr.fetchall()]
        vals['move_line_ids'] = [(6, 0, move_ids)]
        return vals


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

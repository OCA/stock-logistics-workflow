# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _


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

    @api.multi
    def _get_invoice_view_xmlid(self):
        for picking in self.filtered('invoice_id'):
            if picking.invoice_id.type in ('in_invoice', 'in_refund'):
                picking.invoice_view_xmlid = 'account.invoice_supplier_form'
            else:
                picking.invoice_view_xmlid = 'account.invoice_form'

    invoice_id = fields.Many2one(comodel_name='account.invoice',
                                 string='Invoice', readonly=True)
    invoice_view_xmlid = fields.Char(compute='_get_invoice_view_xmlid',
                                     string="Invoice View XMLID",
                                     readonly=True)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_ids = fields.One2many(
        comodel_name='stock.picking', inverse_name='invoice_id',
        string='Related Pickings', readonly=True, copy=False,
        help="Related pickings "
             "(only when the invoice has been generated from the picking).")

    @api.multi
    def unlink(self):
        if any([x and x != 'cancel' for x in
                self.mapped('picking_ids.state')]):
            raise exceptions.Warning(
                _('The picking(s) %s should be cancelled before deleting the'
                  ' invoice.') % ', '.join(self.mapped('picking_ids.name')))
        return super(AccountInvoice, self).unlink()

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        self.mapped('picking_ids').write(
            {'invoice_state': '2binvoiced'})
        return res

    @api.multi
    def action_cancel_draft(self):
        res = super(AccountInvoice, self).action_cancel_draft()
        self.mapped('picking_ids').write(
            {'invoice_state': 'invoiced'})
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.One2many(
        comodel_name='stock.move', inverse_name='invoice_line_id',
        string='Related Stock Moves', readonly=True,
        help="Related stock moves "
             "(only when the invoice has been generated from the picking).")

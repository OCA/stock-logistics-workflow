# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_ids = fields.Many2many(
        comodel_name='stock.picking', string='Related Pickings', readonly=True,
        copy=False,
        help="Related pickings "
             "(only when the invoice has been generated from the picking).")

    @api.multi
    def unlink(self):
        invoices = self.filtered(lambda x: x.state == 'draft')
        pickings = invoices.mapped('picking_ids').filtered(
            lambda x: x.state != 'cancel')
        pickings.write({'invoice_state': '2binvoiced'})
        return super(AccountInvoice, self).unlink()

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        pickings = self.mapped('picking_ids').filtered(
            lambda x: x.state != 'cancel')
        pickings.write({'invoice_state': '2binvoiced'})
        return res

    @api.multi
    def action_cancel_draft(self):
        res = super(AccountInvoice, self).action_cancel_draft()
        pickings = self.mapped('picking_ids').filtered(
            lambda x: x.state != 'cancel')
        pickings.write({'invoice_state': 'invoiced'})
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.Many2many(
        comodel_name='stock.move', string='Related Stock Moves', readonly=True,
        copy=False,
        help="Related stock moves "
             "(only when the invoice has been generated from the picking).")

# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import UserError


class StockQuantWizard(models.TransientModel):
    _inherit = 'deposit.stock.quant.wizard'

    @api.model
    def _default_journal(self):
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', 'sale'),
            ('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)

    quants_action = fields.Selection(
        selection_add=[('invoice', 'Regularize and invoice pickings')])
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        default=_default_journal,
        domain="[('type', '=', 'sale'),('company_id', '=', company_id)]",
        required=True)

    @api.model
    def _prepare_invoice(self, picking):
        journal = self.journal_id
        currency = (
            picking.owner_id.property_product_pricelist.currency_id or
            picking.company_id.currency_id
        )
        invoice = self.env['account.invoice'].new({
            'type': 'out_invoice',
            'partner_id': picking.owner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'name': picking.name,
            'origin': picking.name,
            'company_id': picking.company_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.model
    def _prepare_invoice_line(self, move, invoice):
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice.id,
            'product_id': move.product_id.id,
            'quantity': move.product_qty,
            'uom_id': move.product_uom.id,
            'price_unit': move.price_unit,
        })
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        return invoice_line_vals

    def check_forbbiden_pickings(self, pickings):
        forbidden_pickings = pickings.filtered(lambda x: not x.owner_id)
        if forbidden_pickings:
            raise UserError(_('You can not invoice deposit pickings which not '
                              'has an owner'))

    @api.multi
    def open_invoices(self, invoice_ids):
        action = {
            'name': _('Deposit Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('account.invoice_tree').id, 'tree'),
                (self.env.ref('account.invoice_form').id, 'form'),
            ],
            'domain': [('id', 'in', invoice_ids)],
        }
        return action

    def _invoice_regularized_pickings(self, pickings):
        invoice_ids = []
        for picking in pickings:
            invoice_vals = self._prepare_invoice(picking)
            invoice = self.env['account.invoice'].create(invoice_vals)
            for move in picking.move_lines:
                invoice_line_vals = self._prepare_invoice_line(move, invoice)
                self.env['account.invoice.line'].create(invoice_line_vals)
            invoice.compute_taxes()
            invoice_ids.append(invoice.id)
        if invoice_ids:
            return self.open_invoices(invoice_ids)
        return invoice_ids

    @api.multi
    def action_apply(self):
        if self.quants_action == 'invoice':
            picking_ids = self._regularize_quants(
                self.env.context['active_ids'])
            # Invoice regularized pickings
            invoice_ids = self._invoice_regularized_pickings(
                self.env['stock.picking'].browse(picking_ids))
            return invoice_ids
        return True

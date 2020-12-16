# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class StockBatchPicking(models.Model):
    _inherit = 'stock.picking.batch'

    def action_print_invoices(self):
        invoices = self.mapped('picking_ids.sale_id.invoice_ids')
        if not invoices:
            raise UserError(_('Nothing to print.'))
        report = self.env.ref('account.account_invoices_without_payment')
        return report.report_action(invoices)

    def _get_self_with_context_to_invoice(self):
        to_invoice = self.mapped("picking_ids").filtered(
            lambda r: r.partner_id.batch_picking_auto_invoice)
        return self.with_context(picking_to_invoice_in_batch=to_invoice.ids)

    def done(self):
        self_with_ctx = self._get_self_with_context_to_invoice()
        return super(StockBatchPicking, self_with_ctx).done()

    def action_transfer(self):
        self_with_ctx = self._get_self_with_context_to_invoice()
        return super(StockBatchPicking, self_with_ctx).action_transfer()

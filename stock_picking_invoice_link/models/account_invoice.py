# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2015-2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import base64
from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        string='Related Pickings',
        readonly=True,
        copy=False,
        help="Related pickings "
             "(only when the invoice has been generated from a sale order).",
    )

    def action_invoice_sent(self):
        self.ensure_one()
        attachment_ids = list()
        for picking_id in self.picking_ids:
            pdf = self.env.ref('stock.action_report_picking') \
                .render_qweb_pdf([picking_id.id])[0]
            attachment_ids.append(self.env['ir.attachment'].create({
                'name': picking_id.display_name,
                'type': 'binary',
                'res_id': picking_id.id,
                'res_model': 'stock.picking',
                'datas': base64.b64encode(pdf),
                'mimetype': 'application/x-pdf',
                'datas_fname': "%s.pdf" % picking_id.display_name
            }))
        template = self.env.ref("account.email_template_edi_invoice", False)
        attachment_ids_ids = \
            [attachment_id.id for attachment_id in attachment_ids]
        template.attachment_ids = [(6, 0, attachment_ids_ids)]
        return super(AccountInvoice, self).action_invoice_sent()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.One2many(
        comodel_name='stock.move',
        inverse_name='invoice_line_id',
        string='Related Stock Moves',
        readonly=True,
        copy=False,
        help="Related stock moves "
             "(only when the invoice has been generated from a sale order).",
    )

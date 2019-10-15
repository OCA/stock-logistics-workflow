# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2015-2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


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

    @api.model
    def _refund_cleanup_lines(self, lines):
        result = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        if self.env.context.get('mode') == 'modify':
            for i, line in enumerate(lines):
                for name, field in line._fields.items():
                    if name == 'move_line_ids':
                        result[i][2][name] = [(6, 0, line[name].ids)]
                        line[name] = False
        return result


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.Many2many(
        comodel_name='stock.move',
        relation='stock_move_invoice_line_rel',
        column1='invoice_line_id',
        column2='move_id',
        string='Related Stock Moves',
        readonly=True,
        help="Related stock moves "
             "(only when the invoice has been generated from a sale order).",
    )

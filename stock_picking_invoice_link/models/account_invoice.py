# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_ids = fields.Many2many(
        comodel_name='stock.picking', string='Related Pickings', readonly=True,
        copy=False,
        help="Related pickings "
             "(only when the invoice has been generated from a sale order).")


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.One2many(
        'stock.move', 'invoice_line_id',
        string='Related Stock Moves',
        readonly=True,
        copy=False,
        help="Related stock moves "
             "(only when the invoice has been generated from a sale order).")

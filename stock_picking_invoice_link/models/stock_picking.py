# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_ids = fields.Many2many(
        comodel_name='account.invoice', string='Invoices',
        compute="_compute_invoice_ids")

    @api.multi
    def _compute_invoice_ids(self):
        for picking in self:
            invoices = self.env['account.invoice']
            for line in picking.move_lines:
                invoices |= line.invoice_line_ids.mapped('invoice_id')
            picking.invoice_ids = invoices


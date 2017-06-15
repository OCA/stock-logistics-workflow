# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # Provide this field for backwards compatibility
    invoice_line_ids = fields.Many2many(
        comodel_name='account.invoice.line', string='Invoice Lines',
        compute="_compute_invoice_line_ids")
    invoice_line_id = fields.Many2one(
        comodel_name='account.invoice.line', string='Invoice Line',
        copy=False, readonly=True)

    @api.multi
    @api.depends('invoice_line_id')
    def _compute_invoice_line_ids(self):
        for move in self:
            move.invoice_line_ids = move.invoice_line_id

# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2015-2016 AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    invoice_line_ids = fields.Many2many(
        comodel_name='account.invoice.line', string='Invoice Lines',
        compute="_compute_invoice_line_ids")

    @api.multi
    def _compute_invoice_line_ids(self):
        for move in self:
            if (
                move.procurement_id and move.procurement_id.sale_line_id and
                move.procurement_id.sale_line_id.invoice_lines
            ):
                move.invoice_line_ids = (
                    move.procurement_id.sale_line_id.invoice_lines)
            else:
                move.invoice_line_ids = []

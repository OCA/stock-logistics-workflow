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
        copy=False, readonly=True)
    # Provide this field for backwards compatibility
    invoice_line_id = fields.Many2one(
        comodel_name='account.invoice.line', string='Invoice Line',
        compute="_compute_invoice_line_id")

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_invoice_line_id(self):
        for move in self:
            move.invoice_line_id = move.invoice_line_ids[:1]

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        inv_line_id = super(StockMove, self)._create_invoice_line_from_vals(
            move, invoice_line_vals)
        move.with_context(skip_update_line_ids=True).invoice_line_ids = [
            (4, inv_line_id)]
        move.picking_id.invoice_ids = [(4, invoice_line_vals['invoice_id'])]
        return inv_line_id

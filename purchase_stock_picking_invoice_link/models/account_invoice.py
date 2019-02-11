# Copyright 2019 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _prepare_invoice_line_from_po_line(self, line):
        vals = super()._prepare_invoice_line_from_po_line(line)
        moves = self.env['stock.move'].search([
            ('purchase_line_id', '=', line.id),
        ])
        move_ids = moves._get_moves()
        vals['move_line_ids'] = [(6, 0, move_ids.ids)]
        pickings = move_ids.mapped('picking_id')
        pickings.invoice_ids = [(4, self.id)]
        return vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, vals):
        line = super().create(vals)
        if not line.purchase_line_id:
            return line
        moves = self.env['stock.move'].search([
            ('purchase_line_id', '=', line.purchase_line_id.id),
        ])
        move_ids = moves._get_moves()
        for move in move_ids:
            move.invoice_line_id = line.id
        return line

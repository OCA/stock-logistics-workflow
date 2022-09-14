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
        if moves:
            move_ids = moves._get_moves()
            vals['move_line_ids'] = [(6, 0, move_ids.ids)]
            pickings = move_ids.mapped('picking_id')
            pickings.invoice_ids = [(4, self.id)]
        return vals

    @api.model
    def create(self, values):
        pickings = self.env['stock.picking']
        result = []
        if 'invoice_line_ids' not in values:
            return super().create(values)
        for item in values.get('invoice_line_ids'):
            if not item[2].get('purchase_line_id'):
                continue
            moves = self.env['stock.move'].search([
                ('purchase_line_id', '=', item[2]['purchase_line_id']),
            ])
            if moves:
                move_ids = moves._get_moves()
                item[2]['move_line_ids'] = [(6, 0, move_ids.ids)]
                pickings |= move_ids.mapped('picking_id')
            result.append(item)
        if result and values.get('invoice_line_ids'):
            values['invoice_line_ids'] = result
        res = super().create(values)
        if res:
            for picking in pickings:
                picking.invoice_ids = [(4, res.id)]
        return res

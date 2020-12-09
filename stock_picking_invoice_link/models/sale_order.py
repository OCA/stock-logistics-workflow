# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models
from odoo.tools import float_compare, float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_stock_moves_link_invoice(self):
        moves_linked = self.env["stock.move"]
        for stock_move in self.move_ids:
            if stock_move.state != 'done' or stock_move.scrapped or (
                stock_move.location_dest_id.usage != "customer"
                    and (stock_move.location_id.usage != "customer" or
                         not stock_move.to_refund)):
                continue
            invoice_lines = stock_move.invoice_line_ids.filtered(
                lambda invl: invl.invoice_id.state != "cancel")
            invoiced_qty = 0
            for inv_line in invoice_lines:
                if inv_line.invoice_id.type == 'out_refund':
                    invoiced_qty -= inv_line.quantity
                else:
                    invoiced_qty += inv_line.quantity
            if float_is_zero(invoiced_qty,
                             precision_rounding=self.product_uom.rounding):
                moves_linked += stock_move
        return moves_linked

    def invoice_line_create_vals(self, invoice_id, qty):
        stock_moves = self.get_stock_moves_link_invoice()
        stock_moves.mapped('picking_id').write({
            'invoice_ids': [(4, invoice_id)],
        })
        return super().invoice_line_create_vals(invoice_id, qty)

    def _prepare_invoice_line(self, qty):
        vals = super()._prepare_invoice_line(qty)
        stock_moves = self.get_stock_moves_link_invoice()
        # Invoice returned moves marked as to_refund
        if float_compare(
                qty, 0.0, precision_rounding=self.currency_id.rounding) < 0:
            stock_moves = stock_moves.filtered(lambda m: m.to_refund)
        vals['move_line_ids'] = [(4, m.id) for m in stock_moves]
        return vals

# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_stock_moves_link_invoice(self):
        return self.mapped('move_ids')._filter_for_invoice_link()

    def _prepare_invoice_line(self, qty):
        vals = super()._prepare_invoice_line(qty)
        stock_moves = self.get_stock_moves_link_invoice()
        # Invoice returned moves marked as to_refund
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )
        if float_compare(
                qty, 0.0, precision_digits=precision) < 0:
            stock_moves = stock_moves.filtered(
                lambda m: m.to_refund and not m.invoice_line_ids)
        vals['move_line_ids'] = [(4, m.id) for m in stock_moves]
        return vals

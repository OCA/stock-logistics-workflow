# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_stock_moves_link_invoice(self):
        return self.mapped('move_ids').filtered(
            lambda x: (
                x.state == 'done' and not (any(
                    inv.state != 'cancel' for inv in x.invoice_line_ids.mapped(
                        'invoice_id'))) and not x.scrapped and (
                    x.location_dest_id.usage == 'customer' or
                    (x.location_id.usage == 'customer' and
                     x.to_refund))
            )
        )

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
            stock_moves = stock_moves.filtered(
                lambda m: m.to_refund and not m.invoice_line_ids)
        vals['move_line_ids'] = [(4, m.id) for m in stock_moves]
        return vals

# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
from odoo.tools import float_compare, float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def get_stock_moves_link_invoice(self):
        moves_linked = self.env["stock.move"]
        for stock_move in self.move_ids:
            if (
                stock_move.state != "done"
                or stock_move.scrapped
                or (
                    stock_move.location_id.usage != "supplier"
                    and (
                        stock_move.location_dest_id.usage != "supplier"
                        or not stock_move.to_refund
                    )
                )
            ):
                continue
            invoice_lines = stock_move.invoice_line_ids.filtered(
                lambda invl: invl.move_id.state != "cancel"
                and invl.move_id.type in {"in_invoice", "in_refund"}
            )
            invoiced_qty = 0
            for inv_line in invoice_lines:
                if inv_line.move_id.type == "in_refund":
                    invoiced_qty -= inv_line.quantity
                else:
                    invoiced_qty += inv_line.quantity
            if float_is_zero(
                invoiced_qty, precision_rounding=self.product_uom.rounding
            ):
                moves_linked += stock_move
        return moves_linked

    def _prepare_account_move_line(self, move):
        vals = super()._prepare_account_move_line(move)
        stock_moves = self.get_stock_moves_link_invoice()
        # Invoice returned moves marked as to_refund
        if (
            float_compare(
                self.product_qty - self.qty_invoiced,
                0.0,
                precision_rounding=self.currency_id.rounding,
            )
            < 0
        ):
            stock_moves = stock_moves.filtered("to_refund")
        vals["move_line_ids"] = [(4, m.id) for m in stock_moves]
        return vals

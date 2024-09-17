# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
from odoo.tools import float_compare, float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def get_stock_moves_link_invoice(self):
        moves_linked = self.env["stock.move"]
        if self.product_id.purchase_method == "purchase":
            to_invoice = self.product_qty - self.qty_invoiced
        else:
            to_invoice = self.qty_received - self.qty_invoiced
        for stock_move in self.move_ids.sorted(
            lambda m: (m.write_date, m.id), reverse=True
        ):
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
            if not stock_move.invoice_line_ids:
                to_invoice -= (
                    stock_move.quantity
                    if not stock_move.to_refund
                    else -stock_move.quantity
                )
                moves_linked += stock_move
                continue
            elif float_is_zero(
                to_invoice, precision_rounding=self.product_uom.rounding
            ):
                break
            to_invoice -= (
                stock_move.quantity
                if not stock_move.to_refund
                else -stock_move.quantity
            )
            moves_linked += stock_move
        return moves_linked

    def _prepare_account_move_line(self, move=False):
        vals = super()._prepare_account_move_line(move=move)
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

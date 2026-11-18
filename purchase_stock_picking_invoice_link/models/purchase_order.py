# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def get_stock_moves_link_invoice(self):
        moves_linked = self.env["stock.move"]
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
            if stock_move.invoice_line_ids:
                # The move is already linked to one or more invoice lines.
                # Re-add it only if its done qty is not fully claimed by
                # those lines (legitimate case: one picking split across
                # several invoices of the same PO line). Otherwise skip
                # to avoid over-linking pickings into unrelated invoices.
                # Net the claim against credit notes so a fully-refunded
                # move counts as unclaimed again.
                claimed = 0.0
                for inv_line in stock_move.invoice_line_ids:
                    if (
                        inv_line.purchase_line_id != self
                        or inv_line.parent_state == "cancel"
                    ):
                        continue
                    sign = 1 if inv_line.move_id.move_type == "in_invoice" else -1
                    claimed += sign * inv_line.product_uom_id._compute_quantity(
                        inv_line.quantity, stock_move.product_uom
                    )
                if (
                    float_compare(
                        stock_move.quantity_done - claimed,
                        0.0,
                        precision_rounding=stock_move.product_uom.rounding,
                    )
                    <= 0
                ):
                    continue
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

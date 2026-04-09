# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        """Method used to associate the stock.move with the created account.move.line
        when the invoicing method of the product is 'purchase' and the invoice is done
        before receiving the products.
        """
        res = super().write(vals)
        if vals.get("state", "") == "done":
            stock_moves = self.get_moves_link_invoice()
            invoices_to_recompute = self.env["account.move"]
            for stock_move in stock_moves.filtered(
                lambda sm: sm.purchase_line_id
                and sm.product_id.purchase_method == "purchase"
            ):
                # Use location direction to determine invoice type, not to_refund.
                # In V19, stock_account sets to_refund=True by default for all moves,
                # so to_refund cannot be used to distinguish receipts from returns.
                if stock_move.location_dest_id.usage in ("supplier", "transit"):
                    inv_type = "in_refund"
                else:
                    inv_type = "in_invoice"
                inv_lines = (
                    self.env["account.move.line"]
                    .sudo()
                    .search(
                        [
                            ("purchase_line_id", "=", stock_move.purchase_line_id.id),
                            ("move_id.move_type", "=", inv_type),
                            ("move_id.state", "!=", "cancel"),
                        ]
                    )
                )
                if inv_lines:
                    stock_move.invoice_line_ids = [Command.set(inv_lines.ids)]
                    invoices_to_recompute |= inv_lines.move_id
            if invoices_to_recompute:
                invoices_to_recompute._compute_picking_ids()
        return res

    def get_moves_link_invoice(self):
        return self.filtered(
            lambda x: x.state == "done"
            and not x.scrap_id
            and (
                x.location_id.usage in ("supplier", "transit")
                or x.location_dest_id.usage in ("supplier", "transit")
            )
        )

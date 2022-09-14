# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("state", "") == "done":
            stock_moves = self.get_moves_link_invoice()
            for stock_move in stock_moves.filtered("purchase_line_id"):
                inv_type = stock_move.to_refund and "in_refund" or "in_invoice"
                inv_line = self.env["account.move.line"].search(
                    [
                        ("purchase_line_id", "=", stock_move.purchase_line_id.id),
                        ("move_id.type", "=", inv_type),
                    ]
                )
                if inv_line:
                    stock_move.invoice_line_ids = [(4, m.id) for m in inv_line]
        return res

    def get_moves_link_invoice(self):
        return self.filtered(
            lambda x: x.state == "done"
            and not x.scrapped
            and (
                x.location_id.usage == "supplier"
                or (x.location_dest_id.usage == "supplier" and x.to_refund)
            )
        )

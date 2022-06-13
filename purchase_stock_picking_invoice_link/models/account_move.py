# Copyright 2019 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        for move in res:
            for line in move.invoice_line_ids.filtered("purchase_line_id"):
                stock_moves = self.env["stock.move"].search(
                    [
                        ("purchase_line_id", "=", line.purchase_line_id.id),
                        ("to_refund", "=", (move.move_type == "in_refund")),
                    ]
                )
                if stock_moves:
                    stock_moves = stock_moves.get_moves_link_invoice()
                    line.move_line_ids = [(6, 0, stock_moves.ids)]
        return res

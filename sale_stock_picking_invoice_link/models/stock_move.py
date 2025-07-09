# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2015-2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2025 Akretion - Renato Lima <renato.lima@akretion.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        """
        User can update any picking in done state, but if this picking already
        invoiced the stock move done quantities can be different to invoice
        line quantities. So to avoid this inconsistency you can not update any
        stock move line in done state and have invoice lines linked.
        """
        res = super().write(vals)
        if vals.get("state", "") == "done":
            stock_moves = self.get_moves_delivery_link_invoice()
            for stock_move in stock_moves.filtered(
                lambda sm: sm.sale_line_id and sm.product_id.invoice_policy == "order"
            ):
                inv_type = stock_move.to_refund and "out_refund" or "out_invoice"
                inv_lines = (
                    self.env["account.move.line"]
                    .sudo()
                    .search(
                        [
                            ("sale_line_ids", "=", stock_move.sale_line_id.id),
                            ("move_id.move_type", "=", inv_type),
                        ]
                    )
                )
                if inv_lines:
                    stock_move.invoice_line_ids = [Command.set(inv_lines.ids)]
        return res

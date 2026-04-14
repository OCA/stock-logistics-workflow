# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        """Method used to associate the stock.move with the created account.move.line
        when the invoicing method of the product is 'purchase' and the invoice is done
        before receiving the products.
        """
        res = super()._action_done(cancel_backorder=cancel_backorder)
        stock_moves = res.get_moves_link_invoice()
        for stock_move in stock_moves.filtered(
            lambda sm: sm.purchase_line_id
            and sm.product_id.purchase_method == "purchase"
        ):
            inv_type = (
                "in_refund"
                if stock_move.location_dest_id.usage == "supplier"
                else "in_invoice"
            )
            inv_line = self.env["account.move.line"].search(
                [
                    ("purchase_line_id", "=", stock_move.purchase_line_id.id),
                    ("move_id.move_type", "=", inv_type),
                ]
            )
            if inv_line:
                stock_move.invoice_line_ids = [(4, m.id) for m in inv_line]
        return res

    def get_moves_link_invoice(self):
        return self.filtered(
            lambda x: x.state == "done"
            and not getattr(x, "scrapped", getattr(x, "is_scrap", False))
            and (
                x.location_id.usage == "supplier"
                or (x.location_dest_id.usage == "supplier" and x.to_refund)
            )
        )

# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        """Associate the stock.move with the related account.move.line when the
        invoicing method of the product is 'purchase' and a matching invoice
        line still has quantity not covered by previously linked moves.

        Each move is linked at most to one invoice line (the oldest one whose
        pending quantity is still positive). This avoids over-linking the same
        move to multiple partial invoices of the same purchase order line,
        while preserving the legitimate accumulation case where a single
        invoice with the ordered quantity receives goods through several
        pickings. Cancelled invoices are excluded from the search so an
        abandoned draft does not absorb the newly done move.

        The hook only fires when ``state`` appears in ``vals``. The core
        ``_action_done`` flow writes ``{'state': 'done', 'date': ...}`` to
        the validated moves; this method relies on that contract.
        """
        res = super().write(vals)
        if vals.get("state", "") == "done":
            stock_moves = self.get_moves_link_invoice()
            for stock_move in stock_moves.filtered(
                lambda sm: sm.purchase_line_id
                and sm.product_id.purchase_method == "purchase"
            ):
                inv_type = stock_move.to_refund and "in_refund" or "in_invoice"
                inv_lines = self.env["account.move.line"].search(
                    [
                        ("purchase_line_id", "=", stock_move.purchase_line_id.id),
                        ("move_id.move_type", "=", inv_type),
                        ("move_id.state", "not in", ("cancel",)),
                    ],
                    order="id",
                )
                candidate = inv_lines.filtered(
                    lambda line: stock_move not in line.move_line_ids
                    and float_compare(
                        sum(
                            sm.product_uom._compute_quantity(
                                sm.product_uom_qty, line.product_uom_id
                            )
                            for sm in line.move_line_ids
                        ),
                        line.quantity,
                        precision_rounding=line.product_uom_id.rounding,
                    )
                    < 0
                )[:1]
                if candidate:
                    stock_move.invoice_line_ids = [(4, candidate.id)]
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

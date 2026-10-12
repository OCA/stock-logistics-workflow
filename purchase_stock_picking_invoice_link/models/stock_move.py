# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


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
            for stock_move in stock_moves.filtered(
                lambda sm: sm.purchase_line_id
                and sm.product_id.purchase_method == "purchase"
            ):
                inv_type = stock_move.to_refund and "in_refund" or "in_invoice"
                inv_line = self.env["account.move.line"].search(
                    [
                        ("purchase_line_id", "=", stock_move.purchase_line_id.id),
                        ("move_id.move_type", "=", inv_type),
                    ]
                )
                if inv_line:
                    stock_move.invoice_line_ids = [(4, m.id) for m in inv_line]
        return res

    def _is_purchase_invoice_link_candidate(self):
        """Whether this move can be linked to a vendor bill or refund.

        Accepted endpoints:
        - supplier locations (standard PO receipts/returns)
        - transit locations (intercompany flows route through transit)
        - subcontracting locations (receipts from a subcontractor; the
          location is internal but flagged via ``is_subcontracting_location``,
          which is provided by ``mrp_subcontracting`` when installed)
        """
        self.ensure_one()
        if self.state != "done" or self.scrapped:
            return False
        accepted_usages = ("supplier", "transit")
        if self.location_id.usage in accepted_usages or getattr(
            self.location_id, "is_subcontracting_location", False
        ):
            return True
        if self.to_refund and (
            self.location_dest_id.usage in accepted_usages
            or getattr(self.location_dest_id, "is_subcontracting_location", False)
        ):
            return True
        return False

    def get_moves_link_invoice(self):
        return self.filtered(lambda m: m._is_purchase_invoice_link_candidate())

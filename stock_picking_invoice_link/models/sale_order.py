# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_stock_moves_link_invoice(self):
        skip_check_invoice_state = self.env.context.get(
            "skip_check_invoice_state", False
        )
        return self.mapped("move_ids").filtered(
            lambda mv: (
                mv.state == "done"
                and not (
                    not skip_check_invoice_state
                    and any(
                        inv.state != "cancel"
                        for inv in mv.invoice_line_ids.mapped("move_id")
                    )
                )
                and not mv.scrapped
                and (
                    mv.location_dest_id.usage == "customer"
                    or (mv.location_id.usage == "customer" and mv.to_refund)
                )
            )
        )

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        stock_moves = self.get_stock_moves_link_invoice()
        # Invoice returned moves marked as to_refund
        if (
            float_compare(
                self.qty_to_invoice, 0.0, precision_rounding=self.currency_id.rounding
            )
            < 0
        ):
            stock_moves = stock_moves.filtered(
                lambda m: m.to_refund and not m.invoice_line_ids
            )
        vals["move_line_ids"] = [(4, m.id) for m in stock_moves]
        return vals

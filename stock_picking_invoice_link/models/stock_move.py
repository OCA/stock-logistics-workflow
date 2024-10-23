# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2015-2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        relation="stock_move_invoice_line_rel",
        column1="move_id",
        column2="invoice_line_id",
        string="Invoice Line",
        copy=False,
        readonly=True,
    )

    def write(self, vals):
        """
        User can update any picking in done state, but if this picking already
        invoiced the stock move done quantities can be different to invoice
        line quantities. So to avoid this inconsistency you can not update any
        stock move line in done state and have invoice lines linked.
        """
        if "product_uom_qty" in vals and not self.env.context.get(
            "bypass_stock_move_update_restriction"
        ):
            for move in self.filtered(
                lambda x: float_compare(
                    x.product_uom_qty,
                    vals.get("product_uom_qty") or 0.0,
                    precision_rounding=x.product_uom.rounding,
                )
                != 0
            ):
                if move.state == "done" and move.invoice_line_ids:
                    raise UserError(_("You can not modify an invoiced stock move"))
        res = super().write(vals)
        if vals.get("state", "") == "done":
            stock_moves = self.get_moves_delivery_link_invoice()
            for stock_move in stock_moves.filtered(
                lambda sm: sm.sale_line_id and sm.product_id.invoice_policy == "order"
            ):
                inv_type = stock_move.to_refund and "out_refund" or "out_invoice"
                inv_line = (
                    self.env["account.move.line"]
                    .sudo()
                    .search(
                        [
                            ("sale_line_ids", "=", stock_move.sale_line_id.id),
                            ("move_id.move_type", "=", inv_type),
                        ]
                    )
                )
                if inv_line:
                    stock_move.invoice_line_ids = [(4, m.id) for m in inv_line]
        return res

    def get_moves_delivery_link_invoice(self):
        return self.filtered(
            lambda x: x.state == "done"
            and not x.scrapped
            and (
                x.location_id.usage == "internal"
                or (x.location_dest_id.usage == "internal" and x.to_refund)
            )
        )

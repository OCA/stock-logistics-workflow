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
            for move in self:
                if move.state == "done" and move.invoice_line_ids:
                    raise UserError(_("You can not modify an invoiced stock move"))
        return super().write(vals)

    def _filter_for_invoice_link(self):
        return self.filtered(
            lambda x: (
                x.state == "done"
                and not (
                    any(
                        inv.state != "cancel"
                        for inv in x.invoice_line_ids.mapped("move_id")
                    )
                )
                and not x.scrapped
                and (
                    x.location_dest_id.usage == "customer"
                    or (x.location_id.usage == "customer" and x.to_refund)
                )
            )
        )

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder)
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        moves = self._filter_for_invoice_link()
        # Add extra filtering on products with invoice_policy = delivery as
        # the link was already set at invoice creation
        for move in moves.filtered(lambda m: m.product_id.invoice_policy != "delivery"):
            if float_compare(
                move.sale_line_id.qty_to_invoice, 0.0, precision_digits=precision
            ) < 0 and (not move.to_refund or move.invoice_line_ids):
                continue
            move.write(
                {
                    "invoice_line_ids": [
                        (4, inv_line.id) for inv_line in move.sale_line_id.invoice_lines
                    ]
                }
            )
        return res

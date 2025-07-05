from odoo import _, api, fields, models
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = "account.move"

    is_picking_matched = fields.Boolean(
        compute="_compute_is_picking_matched", store=True
    )

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.move_line_ids",
        "invoice_line_ids.move_line_ids.product_uom_qty",
        "invoice_line_ids.quantity",
    )
    def _compute_is_picking_matched(self):
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            move.is_picking_matched = True
            for line in move.invoice_line_ids:
                qty_matched = sum(
                    stock_move.product_uom_qty for stock_move in line.move_line_ids
                )
                if (
                    float_compare(
                        qty_matched, line.quantity, precision_rounding=precision_digits
                    )
                    < 0
                ):
                    move.is_picking_matched = False
                    break

    def action_picking_matching(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Picking Matching"),
            "res_model": "picking.bill.line.match",
            "domain": [
                (
                    "partner_id",
                    "in",
                    (self.partner_id | self.partner_id.commercial_partner_id).ids,
                ),
                ("company_id", "=", self.company_id.id),
                ("account_move_id", "in", (self.id, False)),
                ("product_id", "in", (self.invoice_line_ids.mapped("product_id").ids)),
            ],
            "view_mode": "tree",
            "context": self.env.context,
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    unmatched_qty = fields.Float(compute="_compute_unmatched_qty", store=True)

    move_line_ids = fields.Many2many(
        readonly=False,
    )

    @api.depends("move_line_ids", "quantity", "move_line_ids.product_uom_qty")
    def _compute_unmatched_qty(self):
        for aml in self:
            aml.unmatched_qty = aml.quantity - sum(
                stock_move.product_uom_qty for stock_move in aml.move_line_ids
            )

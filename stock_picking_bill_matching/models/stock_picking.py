from odoo import _, api, fields, models
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_picking_matched = fields.Boolean(
        compute="_compute_is_picking_matched", store=True
    )

    @api.depends(
        "move_ids",
        "move_ids.invoice_line_ids",
        "move_ids.invoice_line_ids.quantity",
        "move_ids.product_uom_qty",
    )
    def _compute_is_picking_matched(self):
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for picking in self:
            picking.is_picking_matched = True
            for line in picking.move_ids:
                qty_matched = sum(aml.quantity for aml in line.invoice_line_ids)
                if (
                    float_compare(
                        qty_matched,
                        line.product_uom_qty,
                        precision_rounding=precision_digits,
                    )
                    < 0
                ):
                    picking.is_picking_matched = False
                    break

    def action_bill_matching(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Bill Matching"),
            "res_model": "picking.bill.line.match",
            "domain": [
                (
                    "partner_id",
                    "in",
                    (self.partner_id | self.partner_id.commercial_partner_id).ids,
                ),
                ("company_id", "=", self.company_id.id),
                ("picking_id", "in", (self.id, False)),
                ("product_id", "in", (self.move_ids.mapped("product_id").ids)),
            ],
            "view_mode": "tree",
            "context": self.env.context,
        }


class StockMove(models.Model):
    _inherit = "stock.move"

    unmatched_qty = fields.Float(compute="_compute_unmatched_qty", store=True)

    @api.depends("invoice_line_ids", "product_uom_qty", "invoice_line_ids.quantity")
    def _compute_unmatched_qty(self):
        for move in self:
            move.unmatched_qty = move.product_uom_qty - sum(
                aml.quantity for aml in move.invoice_line_ids
            )

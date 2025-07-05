# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_picking_matched = fields.Boolean(
        compute="_compute_is_picking_matched", store=True
    )

    @api.depends(
        "order_line.move_ids.picking_id.is_picking_matched",
    )
    def _compute_is_picking_matched(self):
        for po in self:
            if all(
                picking.is_picking_matched
                for picking in po.order_line.move_ids.mapped("picking_id")
            ):
                po.is_picking_matched = True
            else:
                po.is_picking_matched = False

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
                (
                    "picking_id",
                    "in",
                    self.order_line.mapped("move_ids").mapped("picking_id").ids
                    + [False],
                ),
                (
                    "product_id",
                    "in",
                    self.order_line.mapped("move_ids").mapped("product_id").ids,
                ),
            ],
            "view_mode": "tree",
            "context": self.env.context,
        }


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_invoice_lines(self):
        invoice_lines = super()._get_invoice_lines()
        for move in self.move_ids:
            for aml in move.invoice_line_ids:
                invoice_lines |= aml
        return invoice_lines

    @api.depends(
        "qty_received",
        "product_uom_qty",
        "order_id.state",
        "move_ids.invoice_line_ids",
        "move_ids.invoice_line_ids.quantity",
        "move_ids.invoice_line_ids.move_id.state",
    )
    def _compute_qty_invoiced(self):
        """Overriden to depend on stock move_ids"""
        return super()._compute_qty_invoiced()

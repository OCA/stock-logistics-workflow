# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.tools import float_compare, float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    is_picking_matched = fields.Boolean(
        compute="_compute_is_picking_matched", store=True
    )
    force_picking_matched = fields.Boolean(default=False, copy=False)

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.move_line_ids",
        "invoice_line_ids.move_line_ids.product_uom_qty",
        "invoice_line_ids.quantity",
        "force_picking_matched",
    )
    def _compute_is_picking_matched(self):
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            if move.force_picking_matched:
                move.is_picking_matched = True
                continue
            move.is_picking_matched = True
            for line in move.invoice_line_ids.filtered(
                lambda l: l.display_type == "product"
                and l.product_id
                and l.product_id.type == "product"
            ):
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

    def action_force_picking_matched(self):
        self.ensure_one()
        self.force_picking_matched = True

    def action_reset_force_picking_matched(self):
        self.ensure_one()
        self.force_picking_matched = False

    def _get_bill_lines_to_match(self):
        return self.invoice_line_ids.filtered(
            lambda l: l.display_type == "product"
            and l.product_id
            and l.product_id.type == "product"
            and l.unmatched_qty > 0
        )

    def _get_partner_pickings(self):
        return self.env["stock.picking"].search(
            [
                (
                    "partner_id",
                    "in",
                    (self.partner_id | self.partner_id.commercial_partner_id).ids,
                ),
                ("picking_type_code", "=", "incoming"),
                ("state", "not in", ("done", "cancel")),
            ]
        )

    def _auto_match_perfect_pickings(self, bill_lines, pickings):
        picking_lines = pickings.move_ids.filtered(
            lambda m: m.state != "cancel" and m.unmatched_qty > 0
        )

        bill_qty = defaultdict(float)
        pick_qty = defaultdict(float)
        for aml in bill_lines:
            bill_qty[aml.product_id] += aml.unmatched_qty
        for sm in picking_lines:
            pick_qty[sm.product_id] += sm.unmatched_qty

        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for prod in set(bill_qty.keys()) | set(pick_qty.keys()):
            if not float_is_zero(
                bill_qty[prod] - pick_qty[prod], precision_digits=precision
            ):
                return False

        if not bill_qty:
            return False

        for product in bill_qty:
            amls = bill_lines.filtered(lambda l: l.product_id == product)
            sms = picking_lines.filtered(lambda m: m.product_id == product)
            for aml in amls:
                aml.move_line_ids = [Command.link(sm.id) for sm in sms]

        if self.company_id.auto_validate_matched_picking:
            for sm in picking_lines:
                sm.quantity_done = sm.product_uom_qty
            pickings.with_context(cancel_backorder=False)._action_done()

        if hasattr(self.env["stock.move"], "invoice_state"):
            for sm in picking_lines:
                sm.invoice_state = "invoiced"
            for pick in pickings:
                pick.invoice_state = "invoiced"

        if len(pickings) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "view_mode": "form",
                "res_id": pickings.id,
            }
        return {
            "type": "ir.actions.act_window",
            "name": _("Matched Pickings"),
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", pickings.ids)],
        }

    def _auto_create_picking(self):
        open_pos = self.env["purchase.order"].search_count(
            [
                (
                    "partner_id",
                    "in",
                    (self.partner_id | self.partner_id.commercial_partner_id).ids,
                ),
                ("state", "in", ("draft", "sent", "purchase")),
            ]
        )
        if open_pos != 0:
            return False

        self.env.flush_all()
        empty_match = self.env["picking.bill.line.match"].with_context(
            default_account_move_id=self.id
        )
        wizard_action = empty_match.action_add_to_picking()

        wizard = (
            self.env["bill.to.picking.wizard"]
            .with_context(**wizard_action["context"])
            .create(
                {
                    "partner_id": self.partner_id.id,
                    "auto_validate": (self.company_id.auto_validate_matched_picking),
                }
            )
        )
        return wizard.action_add_to_picking()

    def action_picking_matching(self):
        self.ensure_one()
        context = dict(self.env.context, default_account_move_id=self.id)

        if not self.env.context.get("search_default_matched"):
            bill_lines = self._get_bill_lines_to_match()
            if bill_lines:
                pickings = self._get_partner_pickings()
                if pickings:
                    action = self._auto_match_perfect_pickings(bill_lines, pickings)
                    if action:
                        return action
                elif self.company_id.auto_create_picking_on_match:
                    action = self._auto_create_picking()
                    if action:
                        return action

        if self.env.context.get("search_default_matched"):
            linked_sm_ids = self.invoice_line_ids.mapped("move_line_ids").ids
            domain = [
                "|",
                ("account_move_id", "=", self.id),
                ("sm_id", "in", linked_sm_ids),
            ]
            context.update({"hide_match": True})
        else:
            domain = [
                (
                    "partner_id",
                    "in",
                    (self.partner_id | self.partner_id.commercial_partner_id).ids,
                ),
                ("company_id", "=", self.company_id.id),
                ("account_move_id", "in", (self.id, False)),
                (
                    "product_id",
                    "in",
                    self.invoice_line_ids.mapped("product_id").ids,
                ),
            ]
            context.update({"hide_unmatch": True})

        return {
            "type": "ir.actions.act_window",
            "name": _("Picking Matching"),
            "res_model": "picking.bill.line.match",
            "domain": domain,
            "view_mode": "tree",
            "context": context,
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    unmatched_qty = fields.Float(compute="_compute_unmatched_qty", store=True)
    matching_reference = fields.Char("Matching Ref.", readonly=True)

    move_line_ids = fields.Many2many(
        readonly=False,
    )

    @api.depends("move_line_ids", "quantity", "move_line_ids.product_uom_qty")
    def _compute_unmatched_qty(self):
        for aml in self:
            aml.unmatched_qty = aml.quantity - sum(
                stock_move.product_uom_qty for stock_move in aml.move_line_ids
            )

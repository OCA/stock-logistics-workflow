# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

from .picking_bill_line_match import MATCHING_PRECISION

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    is_picking_matched = fields.Boolean(
        compute="_compute_is_picking_matched", store=True
    )
    force_picking_matched = fields.Boolean(default=False, copy=False)
    unmatched_line_count = fields.Integer(
        compute="_compute_matching_counters",
        help="Vendor bill lines still to be matched against a receipt line.",
    )
    matched_picking_line_count = fields.Integer(
        compute="_compute_matching_counters",
        help="Receipt lines linked to this vendor bill.",
    )

    @api.depends(
        "invoice_line_ids.unmatched_qty",
        "invoice_line_ids.quantity",
        "invoice_line_ids.display_type",
        "invoice_line_ids.product_id",
        "invoice_line_ids.move_line_ids",
    )
    def _compute_matching_counters(self):
        """Counters of the smart buttons.

        Deliberately counts LINES, not quantities: the operator's todo list is
        'which lines still need a decision', and per-line quantities are
        already displayed in the matching screen. A partially matched line
        counts as one unmatched line, whether a single unit or the whole line
        is left. Only the matchable lines are counted (see
        ``_get_bill_product_lines``): a bill full of notes and sections, or the
        service lines of a mixed bill, show a counter of zero.
        """
        for move in self:
            move.unmatched_line_count = len(move._get_bill_lines_to_match())
            move.matched_picking_line_count = len(
                move._get_bill_product_lines().mapped("move_line_ids")
            )

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.move_line_ids",
        "invoice_line_ids.move_line_ids.product_uom_qty",
        "invoice_line_ids.quantity",
        "force_picking_matched",
    )
    def _compute_is_picking_matched(self):
        for move in self:
            if move.force_picking_matched:
                move.is_picking_matched = True
                continue
            move.is_picking_matched = True
            for line in move._get_bill_product_lines():
                qty_matched = sum(
                    stock_move.product_uom_qty for stock_move in line.move_line_ids
                )
                # compare with the UoM rounding (compare the digits count as a
                # rounding would swallow every shortage smaller than that
                # magnitude and wrongly report the line as matched)
                if (
                    float_compare(
                        qty_matched,
                        line.quantity,
                        precision_rounding=self._get_matching_rounding(line),
                    )
                    < 0
                ):
                    move.is_picking_matched = False
                    break

    def _get_matching_rounding(self, line):
        """Rounding used to decide whether a bill line is fully matched."""
        if line.product_uom_id:
            return line.product_uom_id.rounding
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return 10**-precision_digits

    def action_force_picking_matched(self):
        self.ensure_one()
        self.force_picking_matched = True

    def action_reset_force_picking_matched(self):
        self.ensure_one()
        self.force_picking_matched = False

    def _get_bill_product_lines(self):
        """Vendor bill lines that take part in the matching.

        Single source of truth for the filtering, so the screen, the smart
        button counters and the matched state can never disagree: only real
        product lines count. The cosmetic lines (sections, notes), the
        tax/payment-term/rounding lines, the lines without a product and the
        services (which never go through stock) are neither matched nor
        counted, and cannot keep a bill unmatched.
        """
        return self.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
            and line.product_id
            and line.product_id.type in ("product", "consu")
        )

    def _get_bill_lines_to_match(self):
        return self._get_bill_product_lines().filtered(
            lambda line: line.unmatched_qty > 0
        )

    def _get_partner_pickings(self):
        """Receipts of the bill partner that can still be reconciled.

        Cancelled pickings are excluded. DONE pickings are included on
        purpose: goods received before the bill arrives is the most common
        case (the bill is often imported days later), and the matching then
        only links them — an already validated receipt is never validated
        again, see ``picking.bill.line.match.action_match_lines``.
        """
        return self.env["stock.picking"].search(
            [
                (
                    "partner_id",
                    "in",
                    (self.partner_id | self.partner_id.commercial_partner_id).ids,
                ),
                ("picking_type_code", "=", "incoming"),
                ("state", "!=", "cancel"),
            ]
        )

    def _get_referenced_candidates(self):
        """Return the ``(bill lines, receipt lines)`` to auto-match.

        The references are read from the matching screen itself (the
        ``matching_reference`` column of ``picking.bill.line.match``), NOT from
        the stored fields on the lines: a localization computes that column in
        SQL (``_get_bill_matching_reference_sql``) and may leave the stored
        fields empty, while the screen — and therefore the operator — sees the
        SQL value. Using the screen's own value is what guarantees the
        automatic matching pairs exactly what is displayed.

        A bill line qualifies only when it carries a NON-EMPTY reference AND a
        receipt line of the same product carries exactly the same reference.
        Everything else stays for the operator: a line with no reference (the
        matching would then fall back to the product-only wildcard) or whose
        reference no receipt carries is never guessed at — a wrong automatic
        match would reconcile the bill against the wrong receipt, which is
        worse than a manual click.
        """
        self.ensure_one()
        bill_lines = self._get_bill_lines_to_match()
        receipt_lines = self.env["stock.move"]
        if not bill_lines:
            return bill_lines, receipt_lines
        pickings = self._get_partner_pickings()
        if not pickings:
            return bill_lines.browse(), receipt_lines

        lines = self.env["picking.bill.line.match"].search(
            [
                ("unmatched_qty", ">", MATCHING_PRECISION),
                ("account_move_id", "in", (self.id, False)),
                "|",
                ("aml_id", "in", bill_lines.ids),
                ("sm_id", "in", pickings.move_ids.ids),
            ]
        )
        bill_rows = lines.filtered(lambda row: row.aml_id and row.matching_reference)
        receipt_rows = lines.filtered(lambda row: row.sm_id and row.matching_reference)
        matched_lines = self.env["account.move.line"]
        for row in bill_rows:
            sources = receipt_rows.filtered(
                lambda receipt: receipt.product_id == row.product_id
                and receipt.matching_reference == row.matching_reference
            )
            if sources:
                matched_lines |= row.aml_id
                receipt_lines |= sources.sm_id
        return matched_lines, receipt_lines

    def _auto_match_referenced_lines(self):
        """Match the bill lines whose reference identifies their receipt(s).

        Runs the very same engine as a manual match
        (``picking.bill.line.match.action_match_lines``) on the restricted,
        unambiguous candidate set from ``_get_referenced_candidates``, so the
        quantity distribution, the links, the backorders and the
        ``invoice_state`` synchronization behave identically. Matching a
        pending receipt validates it (that is the module's reception
        behaviour); an already done receipt is only linked.

        Returns the match lines that were matched. The caller decides whether
        a chatter note is wanted (see ``_notify_auto_match``).
        """
        matched = self.env["picking.bill.line.match"]
        for move in self:
            if not move.company_id.auto_match_referenced_lines:
                continue
            bill_lines, receipt_lines = move._get_referenced_candidates()
            if not bill_lines or not receipt_lines:
                continue
            lines = self.env["picking.bill.line.match"].search(
                [
                    ("unmatched_qty", ">", MATCHING_PRECISION),
                    ("account_move_id", "in", (move.id, False)),
                    "|",
                    ("aml_id", "in", bill_lines.ids),
                    ("sm_id", "in", receipt_lines.ids),
                ]
            )
            if not lines:
                continue
            lines.action_match_lines()
            matched |= lines
        return matched

    def _has_receipt_candidate(self):
        """True when a receipt of the vendor can still absorb a bill line.

        Used by the small shop automation: a receipt exists for one of the
        products still to match (with something left to bill), so the decision
        — and the receipt creation — belongs to the operator.
        """
        self.ensure_one()
        lines = self._get_bill_lines_to_match()
        if not lines:
            return False
        pickings = self._get_partner_pickings()
        if not pickings:
            return False
        products = lines.mapped("product_id")
        return bool(
            pickings.move_ids.filtered(
                lambda move: move.state != "cancel"
                and move.unmatched_qty > MATCHING_PRECISION
                and move.product_id in products
            )
        )

    def _auto_create_picking_for_unmatched_lines(self):
        """Create the missing receipt for the bill lines with nothing to match.

        The small shop case: an imported bill whose goods were never received
        (no purchase order, no receipt), so rather than sending the operator to
        the matching screen to create the receipt by hand, the bill generates
        it through the very same wizard — hence the same traceability (origin
        and chatter on the receipt) and the same optional validation
        (``auto_validate_matched_picking``).

        Deliberately conservative: nothing is created when a purchase order or
        a receipt candidate exists (``_auto_create_picking`` and
        ``_has_receipt_candidate``), because matching an existing document is a
        decision, not a formality.

        Returns the created picking, empty when there was nothing to do.
        """
        self.ensure_one()
        empty = self.env["stock.picking"]
        if not self.company_id.auto_create_picking_on_post:
            return empty
        self.env.flush_all()
        if not self._get_bill_lines_to_match():
            return empty
        if self._has_receipt_candidate():
            return empty
        action = self._auto_create_picking()
        if not action:
            return empty
        # the receipt the wizard generated is the one it linked to this bill
        return self.invoice_line_ids.move_line_ids.picking_id

    def _notify_auto_create_picking(self, picking):
        """Trace, on the bill, the receipt its posting generated."""
        self.ensure_one()
        self.message_post(
            body=_(
                "The receipt %(receipt_link)s was created automatically for the "
                "%(line_count)s bill line(s) that had nothing to match against.",
                receipt_link=picking._get_html_link(),
                line_count=len(picking.move_ids),
            )
        )

    def _notify_auto_match(self, lines):
        """Trace an automatic matching in the bill chatter.

        An accountant-facing automation that moves stock without a click has
        to be auditable: the message names the receipts and the references it
        used, and the lines stay unmatchable from the Matched Items screen.
        """
        self.ensure_one()
        references = sorted({ref for ref in lines.mapped("sm_id.matching_reference")})
        pickings = lines.mapped("sm_id.picking_id")
        self.message_post(
            body=_(
                "%(line_count)s line(s) automatically matched against "
                "%(picking_names)s (references: %(references)s).",
                line_count=len(lines.mapped("aml_id")),
                picking_names=", ".join(pickings.mapped("name")),
                references=", ".join(references) or _("none"),
            )
        )

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        for move in self.filtered(lambda m: m.move_type in ("in_invoice", "in_refund")):
            match_on_post = (
                move.company_id.auto_match_referenced_lines
                and move.company_id.auto_match_referenced_on_post
            )
            create_on_post = move.company_id.auto_create_picking_on_post
            if not (match_on_post or create_on_post):
                continue
            if move.is_picking_matched:
                continue
            # The whole warehouse automation runs inside a savepoint and never
            # raises out of the posting: a locked period, a missing stock or any
            # other warehouse problem must not block the accounting validation.
            # The savepoint keeps the transaction usable for the chatter
            # message even when the failure came from the database.
            try:
                with self.env.cr.savepoint():
                    matched = move._auto_match_referenced_lines()
                    picking = move._auto_create_picking_for_unmatched_lines()
            except (UserError, ValidationError) as error:
                message = error.args[0] if error.args else str(error)
                move.message_post(
                    body=_(
                        "Automatic bill matching failed: %(error_message)s "
                        "Please match the receipts manually.",
                        error_message=message,
                    )
                )
                _logger.warning(
                    "automatic bill matching failed on %s: %s", move.name, message
                )
                continue
            if matched:
                move._notify_auto_match(matched)
            if picking:
                move._notify_auto_create_picking(picking)
        return posted

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

        linked_moves = self.env["stock.move"]
        for product in bill_qty:
            amls = bill_lines.filtered(lambda l: l.product_id == product)
            sms = picking_lines.filtered(lambda m: m.product_id == product)
            linked_moves |= sms
            for aml in amls:
                aml.move_line_ids = [Command.link(sm.id) for sm in sms]

        # the pickings actually matched drive the feedback (and the optional
        # validation): the partner may have other, unrelated open receipts
        linked_pickings = linked_moves.mapped("picking_id")
        if self.company_id.auto_validate_matched_picking:
            # only the receipts that are not done yet get validated: matching
            # an already received picking must not try to validate it twice
            pending = linked_pickings.filtered(
                lambda p: p.state not in ("done", "cancel")
            )
            for sm in pending.move_ids:
                sm.quantity_done = sm.product_uom_qty
            pending.with_context(cancel_backorder=False)._action_done()

        if hasattr(self.env["stock.move"], "invoice_state"):
            for sm in linked_moves:
                sm.invoice_state = "invoiced"
            for pick in linked_pickings:
                pick.invoice_state = "invoiced"

        if len(linked_pickings) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "view_mode": "form",
                "res_id": linked_pickings.id,
            }
        return {
            "type": "ir.actions.act_window",
            "name": _("Matched Pickings"),
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", linked_pickings.ids)],
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
            .with_context(**wizard_action["context"], bill_matching_auto_create=True)
            .create(
                {
                    "partner_id": self.partner_id.id,
                    "auto_validate": (self.company_id.auto_validate_matched_picking),
                }
            )
        )
        # the wizard owns the receipt traceability (origin + chatter message
        # with a link back to this bill): it knows whether it generated the
        # receipt or fed an existing one
        return wizard.action_add_to_picking()

    def _notify_all_matched(self):
        """Toast + reload of the bill when the matching button finds nothing
        left to match.

        Without it, a bill whose lines were all matched by the automatic
        matching (or by the perfect-match shortcut) leaves the operator in
        front of an empty matching screen, wondering whether anything
        happened — or worse, in front of the stale form whose counters did not
        move.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": _("All the lines are matched."),
                "next": {
                    "type": "ir.actions.act_window",
                    "res_model": "account.move",
                    "res_id": self.id,
                    "view_mode": "form",
                    "views": [[False, "form"]],
                    "target": "current",
                },
            },
        }

    def action_picking_matching(self):
        self.ensure_one()
        context = dict(self.env.context, default_account_move_id=self.id)

        if not self.env.context.get("search_default_matched"):
            # 1. reference-driven automatic matching: only the lines whose
            # reference identifies their receipt are consumed (deterministic)
            matched = self._auto_match_referenced_lines()
            if matched:
                self._notify_auto_match(matched)
            # 2. whatever is left still goes through the heuristics below
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
            else:
                # nothing left: say so explicitly instead of opening an empty
                # matching screen (or returning a stale form)
                return self._notify_all_matched()

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
            context.update(
                {
                    "hide_unmatch": True,
                    "search_default_group_product": 1,
                }
            )

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
        """Billed quantity not covered yet, never negative.

        The link between a bill line and the receipts is a plain many2many
        (``stock_picking_invoice_link``), with no quantity per link: when one
        receipt line covers several bill lines (or the other way around), each
        bill line is linked to the whole receipt line and a plain subtraction
        goes negative — a 2-unit bill line linked to a 4-unit receipt shared
        with another 2-unit bill line would read -2, which is meaningless for
        the operator. What matters on the bill side is "how much of my billed
        quantity is still to be covered", which cannot be below zero.

        The receipt side (``stock.move.unmatched_qty``) deliberately keeps its
        sign: a negative there means the receipt was billed beyond what was
        received, which is exactly the anomaly the operator wants to see.
        """
        for aml in self:
            aml.unmatched_qty = max(
                0.0,
                aml.quantity
                - sum(stock_move.product_uom_qty for stock_move in aml.move_line_ids),
            )

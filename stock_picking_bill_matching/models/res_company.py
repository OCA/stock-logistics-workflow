# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_validate_matched_picking = fields.Boolean(
        string="Auto-Validate Generated Pickings",
        default=False,
    )
    auto_create_picking_on_match = fields.Boolean(
        string="Auto-Create Picking on Match",
        default=False,
        help=(
            "If no open picking/PO exists, automatically create a picking "
            "when clicking 'Match Pickings' on a Bill."
        ),
    )
    auto_match_referenced_lines = fields.Boolean(
        string="Auto-Match Referenced Lines",
        default=False,
        help=(
            "Automatically match the vendor bill lines carrying a matching "
            "reference with the receipt lines carrying the SAME reference "
            "(for instance the xPed/nItemPed of a Brazilian NFe — the purchase "
            "order and its line number — or the reference "
            "synthesized by the fiscal document import wizard). Only the "
            "deterministic cases are matched: a line without a reference, or "
            "with no receipt sharing its reference, is left for the operator "
            "— matching validates pending receipts, like a manual match does."
        ),
    )
    auto_match_referenced_on_post = fields.Boolean(
        string="Auto-Match when Posting the Bill",
        default=False,
        help=(
            "Also run the reference auto-matching when a vendor bill is "
            "posted, so an imported bill is reconciled without any manual "
            "step. Requires 'Auto-Match Referenced Lines'."
        ),
    )
    auto_create_picking_on_post = fields.Boolean(
        string="Auto-Create the Receipt when Posting the Bill",
        default=False,
        help=(
            "Small shop flow: when a posted vendor bill has lines with nothing "
            "to match against (no purchase order, no receipt at all for the "
            "vendor), create the missing incoming receipt from those lines. "
            "Nothing is created when a purchase order or a receipt candidate "
            "exists — matching them is the operator's decision. Combined with "
            "'Auto-Validate Generated Pickings', the generated receipt is "
            "validated immediately, so an imported bill results in stock and a "
            "reconciled bill without any manual step."
        ),
    )

# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

RESERVATION_POLICY_SELECTION = [
    ("direct", "Partial"),
    ("line", "All or nothing per line"),
]

RESERVATION_POLICY_HELP = (
    "How stock is reserved for this transfer's lines (stock moves):\n"
    "- Partial: reserve whatever quantity is available (standard behavior).\n"
    "- All or nothing per line: each line (stock move) is reserved only if its "
    "full quantity is available; otherwise that line stays unreserved. The "
    "all-or-nothing rule is applied independently on each line, not on the "
    "transfer as a whole."
)


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    reservation_policy = fields.Selection(
        selection=RESERVATION_POLICY_SELECTION,
        required=True,
        default="direct",
        help=RESERVATION_POLICY_HELP,
    )

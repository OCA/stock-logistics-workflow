# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

BACKORDER_POLICY_SELECTION = [
    ("ask", "Ask"),
    ("always", "Always"),
    ("never", "Never"),
]

BACKORDER_POLICY_HELP = (
    "If set, this overrides the operation type's backorder policy. "
    "Leave empty to use the default operation type behavior.\n"
    "- Ask: the user is always prompted.\n"
    "- Always: backorders are created automatically.\n"
    "- Never: remaining demand is cancelled without prompt."
)


class ResPartner(models.Model):
    _inherit = "res.partner"

    backorder_policy = fields.Selection(
        selection=BACKORDER_POLICY_SELECTION,
        default=False,
        tracking=True,
        help=BACKORDER_POLICY_HELP,
    )

    @api.model
    def _commercial_fields(self):
        # Propagate the backorder policy from the commercial entity to all of
        # its contacts (delivery addresses, etc.).
        return super()._commercial_fields() + ["backorder_policy"]

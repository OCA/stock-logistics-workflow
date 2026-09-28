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

# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_validate_matched_picking = fields.Boolean(
        related="company_id.auto_validate_matched_picking",
        readonly=False,
    )
    auto_create_picking_on_match = fields.Boolean(
        related="company_id.auto_create_picking_on_match",
        readonly=False,
    )

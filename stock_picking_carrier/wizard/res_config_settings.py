# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    carrier_auto_assign_picking = fields.Boolean(
        string="Carrier auto assign",
        related="company_id.carrier_auto_assign_picking",
        readonly=False,
    )

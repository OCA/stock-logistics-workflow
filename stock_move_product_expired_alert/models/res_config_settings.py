# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.TransientModel):

    _inherit = "res.config.settings"

    check_expired_product_alert_team_id = fields.Many2one(
        related="company_id.check_expired_product_alert_team_id",
        readonly=False,
    )

# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    check_expired_product_alert_team_id = fields.Many2one(
        comodel_name="mail.activity.team",
        help="This is the activity team that will be assigned to"
        "alerts related to transfered expired products.",
    )

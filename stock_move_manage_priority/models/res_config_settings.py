# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_move_manage_priority = fields.Boolean(
        related="company_id.stock_move_manage_priority",
        readonly=False,
        store=True,
    )

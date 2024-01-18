# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_move_manage_priority = fields.Boolean(
        string="Manage Move Priority",
        default=False,
    )

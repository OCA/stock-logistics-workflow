# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    package_move_picking_type_id = fields.Many2one(
        related="company_id.package_move_picking_type_id", readonly=False
    )

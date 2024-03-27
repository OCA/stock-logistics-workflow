# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    stock_picking_assign_operator_at_start = fields.Boolean(
        "Assign responsible at stock picking start",
        readonly=False,
        related="company_id.stock_picking_assign_operator_at_start",
    )

# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_picking_return_lot_restrict = fields.Boolean(
        related="company_id.stock_picking_return_lot_restrict",
        readonly=False,
    )

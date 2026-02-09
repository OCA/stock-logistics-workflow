# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_reusable_pack = fields.Boolean(
        help="If checked, 'Put in Pack' will prompt to select a reusable package.",
    )

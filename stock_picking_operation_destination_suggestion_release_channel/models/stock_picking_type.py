# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    suggest_destination_release_channel = fields.Boolean(
        string="Based on same Release Channel",
        help="Check this if you want to suggest destination locations with pending moves"
        "with the same release channel",
    )

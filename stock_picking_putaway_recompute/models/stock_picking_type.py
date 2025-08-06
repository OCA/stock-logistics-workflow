# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    allow_to_recompute_putaways = fields.Boolean(
        help="Check this if you want to authorize putaways recomputations for the "
        "operations of this type."
    )

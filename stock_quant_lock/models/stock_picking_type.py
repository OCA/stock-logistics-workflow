# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    allow_quant_lock = fields.Boolean(
        string="Allow quant lock",
        help="If checked, this operation type can be used to lock stock quants.",
    )

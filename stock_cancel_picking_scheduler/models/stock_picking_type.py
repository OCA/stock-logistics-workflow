# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    cancel_waiting_picking_with_scheduler = fields.Boolean(
        help="Check this if you want to cancel waiting pickings before the"
        "scheduler run."
    )

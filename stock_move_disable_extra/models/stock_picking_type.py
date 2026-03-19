# Copyright (C) 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    disable_extra_moves = fields.Boolean(
        help="If checked, extra moves will not be created when receiving more quantity "
        "than demanded. This preserves lot/serial information but may affect "
        "push rules and backorder handling.",
    )

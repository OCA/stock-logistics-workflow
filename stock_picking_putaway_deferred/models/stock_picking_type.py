# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    defer_putaway_to_operator = fields.Boolean(
        string="Defer Putaway to Operator",
        help=(
            "When enabled, putaway strategies are not applied at reservation time. "
            "The operator must manually apply them (via the 'Recompute Putaways' button) "
            "before the picking can be validated."
        ),
    )

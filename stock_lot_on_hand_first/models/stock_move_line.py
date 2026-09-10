# Copyright 2024 360ERP (<https://www.360erp.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    display_lots_on_hand_first = fields.Boolean(
        related="move_id.display_lots_on_hand_first",
    )

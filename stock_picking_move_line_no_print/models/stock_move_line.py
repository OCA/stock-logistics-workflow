# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    display_in_report = fields.Boolean(related="move_id.display_in_report")

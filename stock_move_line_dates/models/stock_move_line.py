# Copyright 2025 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    date_deadline = fields.Datetime(
        related="move_id.date_deadline",
        string="Deadline",
        store=True,
    )
    scheduled_date = fields.Datetime(store=True)

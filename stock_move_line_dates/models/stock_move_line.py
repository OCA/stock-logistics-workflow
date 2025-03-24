# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    date_schedule = fields.Datetime(
        related="move_id.date",
        string="Date Scheduled",
        store=True,
        readonly=True,
    )
    date_deadline = fields.Datetime(
        related="move_id.date_deadline",
        string="Deadline",
        store=True,
        readonly=True,
    )

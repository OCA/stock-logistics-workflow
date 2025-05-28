# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    display_in_report = fields.Boolean(
        default=True, help="Whether to show it or not to customers in delivery slips"
    )

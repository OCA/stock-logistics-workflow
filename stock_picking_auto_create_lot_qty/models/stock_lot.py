# Copyright Cetmix OU 2024
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    name = fields.Char(
        default=lambda self: self.env["ir.sequence"].next_by_code(
            self.env.company.stock_lot_serial_sequence_id.code
        )
    )

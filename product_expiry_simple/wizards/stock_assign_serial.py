# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockAssignSerialNumbers(models.TransientModel):
    _inherit = "stock.assign.serial"

    serial_expiry_date = fields.Date(string="Expiry Date")
    product_use_expiry_date = fields.Boolean(
        related="move_id.product_id.use_expiry_date"
    )

    def generate_serial_numbers(self):
        self.ensure_one()
        if self.product_use_expiry_date and self.serial_expiry_date:
            self.move_id.serial_expiry_date = self.serial_expiry_date
        else:
            self.move_id.serial_expiry_date = False
        return super().generate_serial_numbers()

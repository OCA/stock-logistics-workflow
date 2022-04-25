# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockAssignSerialNumbers(models.TransientModel):
    _inherit = ["stock.assign.serial", "assign.serial.final.mixin"]
    _name = "stock.assign.serial"
    _next_serial_field = "next_serial_number"

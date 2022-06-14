# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = ["stock.move", "assign.serial.final.mixin"]
    _name = "stock.move"
    _next_serial_field = "next_serial"

    def action_show_details(self):
        self.final_serial_number = False
        return super().action_show_details()

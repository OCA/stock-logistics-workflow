# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # Add fields for the feature that generate serial numbers from first SN + Number of SN
    serial_expiry_date = fields.Date(string="Expiry Date")
    product_use_expiry_date = fields.Boolean(related="product_id.use_expiry_date")

    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        move_lines_commands = super()._generate_serial_move_line_commands(
            lot_names, origin_move_line=origin_move_line
        )
        if self.product_id.use_expiry_date and self.serial_expiry_date:
            for move_line_command in move_lines_commands:
                move_line_command[2]["expiry_date"] = self.serial_expiry_date
        return move_lines_commands

    def action_show_details(self):
        action = super().action_show_details()
        # empty field 'serial_expiry_date' on each run (like next_serial)
        self.serial_expiry_date = False
        return action

# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

import datetime

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    all_expiry_dates_set = fields.Boolean(
        compute="_compute_all_expiry_dates_set",
    )

    def _compute_all_expiry_dates_set(self):
        """Check if all move lines have an expiration date set."""
        for record in self:
            record.all_expiry_dates_set = not record.use_expiration_date or all(
                record.move_line_ids.filtered("qty_done").mapped("expiration_date")
            )

    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        """Override to add a default `expiration_date` into the move lines values."""
        move_lines_commands = super()._generate_serial_move_line_commands(
            lot_names, origin_move_line=origin_move_line
        )
        if not self.product_id.use_expiration_date:
            return move_lines_commands
        # managed by super() until here
        expiration_dtt = False
        if self.product_id.expiration_time > 0:
            expiration_dtt = fields.Datetime.today() + datetime.timedelta(
                days=self.product_id.expiration_time
            )
        for move_line_command in move_lines_commands:
            move_line_command[2]["expiration_date"] = expiration_dtt
        return move_lines_commands

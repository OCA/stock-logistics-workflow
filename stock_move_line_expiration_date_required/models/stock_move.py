# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

import datetime

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    all_expiry_dates_set = fields.Boolean(
        compute="_compute_all_expiry_dates_set",
    )

    def _compute_all_expiry_dates_set(self):
        """Check if all move lines have an expiration date set."""
        for record in self:
            record.all_expiry_dates_set = not record.use_expiration_date or all(
                record.move_line_ids.filtered("quantity").mapped("expiration_date")
            )

    @api.model
    def action_generate_lot_line_vals(
        self, context_data, mode, first_lot, count, lot_text
    ):
        """Override to not default an `expiration_date` on the generated lines."""
        vals_list = super().action_generate_lot_line_vals(
            context_data, mode, first_lot, count, lot_text
        )
        product = self.env["product.product"].browse(
            context_data.get("default_product_id")
        )
        if not product.use_expiration_date or product.expiration_time > 0:
            return vals_list
        if mode == "generate":
            # In generate mode all expiration_dates are defaulting, since
            # no expiration_time, these will be wrongly set dates. Setting
            # them to False.
            for vals in vals_list:
                vals["expiration_date"] = False
            return vals_list
        # In import mode, users can import expiration dates.
        # Lines with no expiration_date get their date defaulted, so we need
        # to set to False only the lines for which no date was given during import.
        for vals, lot in zip(vals_list, self.split_lots(lot_text), strict=False):
            if not lot.get("expiration_date"):
                vals["expiration_date"] = False
        return vals_list

    def _generate_serial_move_line_commands(
        self, field_data, location_dest_id=False, origin_move_line=None
    ):
        """Override to add a default `expiration_date` into the move lines values."""
        move_lines_commands = super()._generate_serial_move_line_commands(
            field_data,
            location_dest_id=location_dest_id,
            origin_move_line=origin_move_line,
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

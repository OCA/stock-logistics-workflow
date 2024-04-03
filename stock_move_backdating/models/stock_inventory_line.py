#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        res = super()._get_move_values(qty, location_id, location_dest_id, out)
        date_backdating = self.inventory_id.date_backdating
        if date_backdating:
            move_line_ids = res.get("move_line_ids", list())
            for move_line_values in move_line_ids:
                # Extract the dictionary from (0, 0, <dict>)
                move_line_values = move_line_values[2]
                move_line_values["date_backdating"] = date_backdating
        return res

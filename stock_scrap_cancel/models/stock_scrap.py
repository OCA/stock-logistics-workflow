# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    state = fields.Selection(selection_add=([("cancel", "Cancelled")]))

    def action_draft(self):
        return self.write({"state": "draft"})

    def action_cancel(self):
        """We need to change the state of the move to draft in order to delete it
        (a done move cannot be deleted)."""
        old_scrap_qty = self.scrap_qty
        self.move_ids.move_line_ids.write({"quantity": 0.0})
        self.move_ids.write({"state": "draft"})
        self.move_ids.unlink()
        return self.write(
            {"state": "cancel", "scrap_qty": old_scrap_qty, "date_done": False}
        )

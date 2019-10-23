# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_life_date = fields.Datetime(
        string="End of Life Date",
        related="lot_id.life_date",
    )

    def action_select_move_line(self):
        """Set the move line as the current one at the picking level."""
        self.ensure_one()
        self.picking_id.reception_screen_id.button_reset()
        self.picking_id.reception_screen_id.current_move_line_id = self
        self.picking_id.reception_screen_id.current_move_id = self.move_id
        self.picking_id.reception_screen_id.next_step()
        # FIXME: don't know how to close the pop-up and refresh the screen
        return self.picking_id.action_reception_screen_open()

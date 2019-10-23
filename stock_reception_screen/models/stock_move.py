# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    reception_screen_current_step = fields.Char(
        related="picking_id.reception_screen_id.current_step")

    def action_select_product(self):
        """"Same than `action_select_move` excepting that as we we are in the
        'select_product' step and that the user already selected the right
        move through this button, we automatically go to the next step
        (done by `process_select_product`).
        """
        self.picking_id.reception_screen_id.current_move_id = self
        self.picking_id.reception_screen_id.process_select_product()

    def action_select_move(self):
        """Set the move as the current one at the picking level."""
        self.ensure_one()
        # self.picking_id.reception_screen_id.button_reset()
        self.picking_id.reception_screen_id.current_move_id = self
        self.picking_id.reception_screen_id.process_select_move()
        return True

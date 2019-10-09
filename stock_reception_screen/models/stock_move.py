# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_select_move(self):
        """Set the move as the current one at the picking level."""
        self.ensure_one()
        self.picking_id.button_cancel_step()
        self.picking_id.current_move_id = self
        self.picking_id.next_step()
        return True

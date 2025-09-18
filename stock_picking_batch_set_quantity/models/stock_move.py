# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_set_quantity(self):
        self.ensure_one()
        self._action_assign()
        if self.quantity:
            self.state = "done"

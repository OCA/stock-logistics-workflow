# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_set_quantities_to_reservation(self):
        """Public method to be called from button"""
        self._set_quantities_to_reservation()

# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "stock.actual.date.mixin"]

    def _get_actual_date_update_triggers(self):
        return super()._get_actual_date_update_triggers() + ["date_done", "move_ids"]

    def _get_stock_moves(self):
        self.ensure_one()
        # Scrap moves follow their scrap's actual_date, not the picking's.
        return self.move_ids.filtered(lambda m: not m.scrap_id)

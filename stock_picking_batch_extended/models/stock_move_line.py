# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _add_to_wave(self, wave=False):
        super()._add_to_wave(wave)
        return self.env["stock.picking.to.batch"].action_view_batch_picking(
            self.batch_id
        )

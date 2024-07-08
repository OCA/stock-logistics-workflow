# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def _create_correction_svl(self, move, diff):
        if move._is_in() and diff < 0:
            move = move.with_context(origin_returned_moves=move)
        return super()._create_correction_svl(move, diff)

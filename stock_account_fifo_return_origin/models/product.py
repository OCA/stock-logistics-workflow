# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _get_fifo_candidates(self, company, lot=False):
        candidates = super()._get_fifo_candidates(company, lot=lot)
        origin_move = self.env.context.get("origin_returned_move")
        if not origin_move:
            return candidates
        origin_svl = origin_move.stock_valuation_layer_ids.filtered(
            lambda x: x.remaining_qty > 0.00
        )
        return origin_svl | candidates

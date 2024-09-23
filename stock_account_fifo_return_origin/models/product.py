# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _get_fifo_candidates(self, company):
        candidates = super()._get_fifo_candidates(company)
        returned_moves = self.env.context.get("origin_returned_moves")
        if not returned_moves:
            return candidates
        returned_moves = returned_moves.filtered(lambda x: x.product_id == self)
        origin_svl = returned_moves.stock_valuation_layer_ids.filtered(
            lambda x: x.remaining_qty > 0.00
        )
        candidates = origin_svl | candidates
        return candidates

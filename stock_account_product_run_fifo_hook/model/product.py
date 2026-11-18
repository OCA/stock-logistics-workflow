# Copyright 2026 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from datetime import datetime, timedelta

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_prepare_candidate_update(
        self, candidate_move, qty_taken, value_taken, valued_move
    ):
        return True

    def _run_fifo_correction_reset(self, valued_moves):
        return True

    def _correct_inventory_valuation(self, from_date):
        boundary = from_date
        if from_date != datetime.min:  # noqa: DTZ901
            boundary = from_date - timedelta(seconds=1)
        fifo_products = self.filtered(lambda product: product.cost_method == "fifo")
        moves_by_product = fifo_products._get_stock_moves_with_valuation_by_product(
            boundary
        )
        moves_out = (
            self.env["stock.move"].concat(moves_by_product.values()).filtered("is_out")
        )
        if moves_out:
            fifo_products._run_fifo_correction_reset(moves_out)
        return super()._correct_inventory_valuation(from_date)

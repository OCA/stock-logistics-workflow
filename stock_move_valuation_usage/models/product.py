# 2026 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_prepare_candidate_update(
        self, candidate_move, qty_taken, value_taken, valued_move
    ):
        res = super()._run_fifo_prepare_candidate_update(
            candidate_move, qty_taken, value_taken, valued_move
        )
        if valued_move and qty_taken > 0:
            self.env["stock.move"]._create_usage_record(
                src_move=candidate_move,
                dest_move=valued_move,
                quantity=qty_taken,
                value=value_taken,
            )
        return res

    def _run_fifo_correction_reset(self, valued_moves):
        res = super()._run_fifo_correction_reset(valued_moves)
        # The FIFO replay creates the usage records of these moves again
        valued_moves.sudo().incoming_usage_ids.unlink()
        return res

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
        # Create usage records only during move validation
        if valued_move and qty_taken > 0 and valued_move.state != "done":
            self.env["stock.move"]._create_usage_record(
                src_move=candidate_move,
                dest_move=valued_move,
                quantity=qty_taken,
                value=value_taken,
            )
        return res

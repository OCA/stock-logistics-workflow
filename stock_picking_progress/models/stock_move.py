# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    progress = fields.Float(compute="_compute_progress", store=True, aggregator="avg")

    @api.depends(
        "picked",
        "product_uom",
        "product_uom_qty",
        "state",
        # Move line's fields used by method ``_get_picked_quantity()``: we add them
        # to make sure the progress is recomputed when the picked quantity changes
        "move_line_ids.picked",
        "move_line_ids.product_uom_id",
        "move_line_ids.quantity",
    )
    def _compute_progress(self):
        for move in self:
            qty = move.product_uom_qty
            # Done moves or moves with no demanded quantity are considered as 100% done
            if move.state == "done" or float_is_zero(
                qty, precision_rounding=move.product_uom.rounding
            ):
                move.progress = 100
            # Picked moves' progress is computed using the picked qty
            elif move.picked:
                move.progress = 100 * move._get_picked_quantity() / qty
            # All other moves have 0% progress
            else:
                move.progress = 0

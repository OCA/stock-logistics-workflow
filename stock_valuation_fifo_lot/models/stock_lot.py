# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    is_force_fifo_candidate = fields.Boolean(
        compute="_compute_is_force_fifo_candidate",
        store=True,
        help="Technical field to indicate that the lot has no on-hand quantity but has "
        "a remaining value in FIFO valuation terms.",
    )

    @api.depends(
        "quant_ids.quantity", "product_id.stock_move_ids.move_line_ids.qty_remaining"
    )
    def _compute_is_force_fifo_candidate(self):
        for lot in self:
            if lot.product_id.cost_method != "fifo":
                continue
            if not self.env["stock.move.line"].search(
                [("lot_id", "=", lot.id), ("qty_remaining", ">", 0)]
            ):
                continue
            lot.is_force_fifo_candidate = not bool(
                lot.quant_ids.filtered(
                    lambda x: x.location_id.usage == "internal" and x.quantity
                )
            )

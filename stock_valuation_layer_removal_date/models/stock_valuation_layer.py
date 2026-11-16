# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    removal_date = fields.Datetime(
        compute="_compute_removal_date",
        store=True,
        index="btree_not_null",
        compute_sudo=True,
        help="Removal date of the lot/serial of the stock move. When the move "
        "holds several lots, the earliest removal date is kept.",
    )

    @api.depends(
        "lot_id.removal_date",
        "stock_move_id.move_line_ids.lot_id.removal_date",
        "stock_move_id.move_line_ids.quantity",
    )
    def _compute_removal_date(self):
        for layer in self:
            lots = layer.lot_id or layer.stock_move_id.lot_ids
            layer.removal_date = min(
                filter(None, lots.mapped("removal_date")), default=False
            )

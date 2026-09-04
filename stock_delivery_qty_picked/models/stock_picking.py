# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import api, models
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends(
        "move_line_ids",
        "move_line_ids.result_package_id",
        "move_line_ids.product_uom_id",
        "move_line_ids.quantity",
        "move_line_ids.qty_picked",
        "move_line_ids.picked",
    )
    def _compute_bulk_weight(self):
        res = super()._compute_bulk_weight()
        move_lines = self.env["stock.move.line"].search(
            [
                ("picking_id", "in", self.ids),
                ("product_id", "!=", False),
                ("result_package_id", "=", False),
                ("picked", "=", True),
            ]
        )
        adjustments = defaultdict(float)
        for ml in move_lines:
            if (
                float_compare(
                    ml.qty_picked,
                    ml.quantity,
                    precision_rounding=ml.product_uom_id.rounding,
                )
                != 0
            ):
                orig_qty = ml.product_uom_id._compute_quantity(
                    ml.quantity, ml.product_id.uom_id
                )
                actual_qty = ml.product_uom_id._compute_quantity(
                    ml.qty_picked, ml.product_id.uom_id
                )
                adjustments[ml.picking_id.id] += (
                    actual_qty - orig_qty
                ) * ml.product_id.weight
        for picking in self:
            if adjustments.get(picking.id):
                picking.weight_bulk += adjustments[picking.id]
        return res

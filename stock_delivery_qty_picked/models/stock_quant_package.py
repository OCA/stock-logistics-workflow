# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def _get_weight(self, picking_id=False):
        res = super()._get_weight(picking_id=picking_id)
        if not picking_id:
            return res
        move_lines = self.env["stock.move.line"].search(
            [
                ("result_package_id", "in", self.ids),
                ("product_id", "!=", False),
                ("picking_id", "=", picking_id),
                ("picked", "=", True),
            ]
        )
        package_map = {p.id: p for p in res.keys()}
        for ml in move_lines:
            if (
                ml.picked
                and float_compare(
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
                weight_delta = (actual_qty - orig_qty) * ml.product_id.weight
                target_package = package_map.get(ml.result_package_id.id)
                if target_package:
                    res[target_package] += weight_delta
        return res

# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, models


class StockMoveLine(models.Model):
    """Use propagated package counts for variable-quantity reservations."""

    _inherit = "stock.move.line"

    @api.depends(
        "move_id.product_packaging_id",
        "product_uom_id",
        "quantity",
    )
    def _compute_product_packaging_qty(self):
        res = super()._compute_product_packaging_qty()
        for move in self.move_id:
            origin_moves = move.move_orig_ids.filtered(
                "picking_type_id.propagate_variable_qty"
            )
            if not origin_moves:
                continue
            for line in move.move_line_ids:
                source_lines = origin_moves.move_line_ids.filtered(
                    lambda source, line=line: source.location_dest_id
                    == line.location_id
                    and source.lot_id == line.lot_id
                    and source.result_package_id == line.package_id
                    and source.owner_id == line.owner_id
                )
                matching_lines = move.move_line_ids.filtered(
                    lambda candidate, line=line: candidate.location_id
                    == line.location_id
                    and candidate.lot_id == line.lot_id
                    and candidate.package_id == line.package_id
                    and candidate.owner_id == line.owner_id
                )
                if len(source_lines) == len(matching_lines) == 1:
                    # Preserve the package count for an identifiable reservation.
                    line.product_packaging_qty = source_lines.product_packaging_quantity
        return res

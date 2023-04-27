# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.depends(
        "has_tracking",
        "picking_type_id.auto_create_lot",
        "product_id.auto_create_lot",
        "picking_type_id.use_existing_lots",
        "state",
    )
    def _compute_display_assign_serial(self):
        super()._compute_display_assign_serial()
        moves_not_display = self.filtered(
            lambda m: m.picking_type_id.auto_create_lot and m.product_id.auto_create_lot
        )
        for move in moves_not_display:
            move.display_assign_serial = False
        return

    # pylint: disable=missing-return
    def _set_quantities_to_reservation(self):
        super()._set_quantities_to_reservation()
        for move in self:
            if move.state not in ("partially_available", "assigned"):
                continue
            if (
                move.product_id.tracking == "none"
                or not move.product_id.auto_create_lot
                or not move.picking_type_id.auto_create_lot
            ):
                continue
            for move_line in move.move_line_ids:
                if move_line.lot_id:
                    # Create-backorder wizard would open without this.
                    move_line.qty_done = move_line.reserved_uom_qty

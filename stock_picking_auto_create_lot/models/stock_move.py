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

    def _set_quantities_to_reservation(self):
        """Allow complete quantities reservation if the lot will be created when
        the picking has been validated
        """
        res = super()._set_quantities_to_reservation()
        moves_to_process = self.filtered(
            lambda mv: not mv.quantity_done
            and mv.state in ["partially_available", "assigned"]
            and mv.picking_type_id.use_create_lots
            and mv.picking_type_id.auto_create_lot
            and mv.product_id.auto_create_lot
        )
        for move in moves_to_process:
            for move_line in move.move_line_ids:
                if not move_line.lot_name:
                    move_line.qty_done = move_line.product_uom_qty
        return res

# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_set_quantities_to_reservation(self):
        """Public method based on _set_quantities_to_reservation of stock.move model"""
        for move_line in self:
            if move_line.state not in ("partially_available", "assigned"):
                continue
            move = move_line.move_id
            if (
                move.has_tracking == "none"
                or (move.picking_type_id.use_existing_lots and move_line.lot_id)
                or (move.picking_type_id.use_create_lots and move_line.lot_name)
                or (
                    not move.picking_type_id.use_existing_lots
                    and not move.picking_type_id.use_create_lots
                )
            ):
                move_line.qty_done = move_line.product_uom_qty

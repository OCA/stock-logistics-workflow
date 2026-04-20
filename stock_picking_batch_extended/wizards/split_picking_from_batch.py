# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models
from odoo.tools.float_utils import float_compare


class SplitPickingFromBatch(models.TransientModel):
    _name = "split.picking.from.batch"

    move_ids = fields.Many2many("stock.move")
    picking_batch_id = fields.Many2one("stock.picking.batch")

    def split_pickings(self):
        picking_move_backorder = {}
        for move in self.move_ids.sorted("picking_id"):
            rounding = move.product_uom.rounding
            if (
                float_compare(
                    move.quantity, move.product_uom_qty, precision_rounding=rounding
                )
                < 0
            ):
                quantity = move.product_uom_qty - move.quantity
                move_copy = move.copy(
                    {
                        "quantity": quantity,
                        "product_uom_qty": quantity,
                        "picking_id": False,
                    }
                )
                if not picking_move_backorder.get(move.picking_id, False):
                    picking_move_backorder[move.picking_id] = move_copy
                else:
                    picking_move_backorder[move.picking_id] |= move_copy
                move.write(
                    {
                        "product_uom_qty": move.quantity,
                    }
                )

        for picking, moves in picking_move_backorder.items():
            backorder_picking = picking._create_backorder_picking()
            moves.write({"picking_id": backorder_picking.id, "picked": False})
            moves.move_line_ids.package_level_id.write(
                {"picking_id": backorder_picking.id}
            )
            moves.mapped("move_line_ids").write({"picking_id": backorder_picking.id})

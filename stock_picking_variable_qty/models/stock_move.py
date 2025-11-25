# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        self._adjust_variable_quantity()
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _adjust_variable_quantity(self):
        """For moves where quantity ≠ qty_demanded spread that new quantity across every
        move_dest_id.
        """
        moves = self.filtered(
            lambda move: move.move_dest_ids and move.picking_type_id.variable_quantity
        )
        # A destination move can be linked to multiple origins, so it must be
        # recomputed once from the whole connected chain.
        processed_dest_moves = self.env["stock.move"]
        for move in moves:
            dest_moves = (move.move_dest_ids - processed_dest_moves).filtered(
                lambda dest_move: dest_move.state not in {"done", "cancel"}
            )
            if not dest_moves:
                continue
            group_moves, group_dest_moves = move._get_variable_quantity_group(
                dest_moves
            )
            processed_dest_moves |= group_dest_moves
            rounding = move.product_uom.rounding
            new_quantity = sum(group_moves.mapped("quantity"))
            demanded_quantity = sum(group_dest_moves.mapped("product_uom_qty"))
            if (
                float_compare(
                    new_quantity,
                    demanded_quantity,
                    precision_rounding=rounding,
                )
                == 0
            ):
                continue
            qty_left = new_quantity
            original_quantities = {
                move_dest.id: move_dest.product_uom_qty
                for move_dest in group_dest_moves
            }
            for move_dest in group_dest_moves.sorted("id"):
                assignable = 0.0
                if float_compare(qty_left, 0.0, precision_rounding=rounding) > 0:
                    assignable = min(original_quantities[move_dest.id], qty_left)
                move_dest.product_uom_qty = assignable
                qty_left -= assignable
            # Keeping any overflow on a single move avoids fabricating demand on
            # extra moves that were not planned by the route.
            if float_compare(qty_left, 0.0, precision_rounding=rounding) > 0:
                first_dest_move = group_dest_moves.sorted("id")[:1]
                first_dest_move.product_uom_qty += qty_left

    def _get_variable_quantity_group(self, dest_moves):
        group_moves = self
        group_dest_moves = dest_moves
        previous_move_count = previous_dest_count = -1
        while previous_move_count != len(group_moves) or previous_dest_count != len(
            group_dest_moves
        ):
            previous_move_count = len(group_moves)
            previous_dest_count = len(group_dest_moves)
            group_moves |= group_dest_moves.move_orig_ids.filtered(
                lambda move: move.picking_type_id.variable_quantity
                and move.state != "cancel"
            )
            group_dest_moves |= group_moves.move_dest_ids.filtered(
                lambda move: move.state not in {"done", "cancel"}
            )
        return group_moves, group_dest_moves

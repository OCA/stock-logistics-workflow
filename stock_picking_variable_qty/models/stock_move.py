# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        moves = self
        if not cancel_backorder:
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            moves = self.filtered(
                lambda move: not move._needs_variable_quantity_backorder(
                    precision_digits=precision_digits
                )
            )
        moves._adjust_variable_quantity()
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _create_backorder(self):
        # Split moves where necessary and move quants. This mirrors the core
        # implementation so we can keep a reliable source/backorder move mapping.
        backorder_moves_vals = []
        backorder_sources = []
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            if (
                float_compare(
                    move.quantity,
                    move.product_uom_qty,
                    precision_digits=precision_digits,
                )
                < 0
            ):
                qty_split = move.product_uom._compute_quantity(
                    move.product_uom_qty - move.quantity,
                    move.product_id.uom_id,
                    rounding_method="HALF-UP",
                )
                new_move_vals = move._split(qty_split)
                backorder_moves_vals += new_move_vals
                backorder_sources += [move] * len(new_move_vals)
        backorder_moves = self.env["stock.move"].create(backorder_moves_vals)
        backorder_moves.with_context(
            bypass_entire_pack=True, bypass_procurement_creation=True
        )._action_confirm(merge=False)
        self._split_variable_quantity_dest_moves(backorder_sources, backorder_moves)
        return backorder_moves

    def _needs_variable_quantity_backorder(self, precision_digits=None):
        self.ensure_one()
        if not (
            self.move_dest_ids
            and self.picking_type_id.variable_quantity
            and self.picked
            and self.quantity > 0
        ):
            return False
        precision_digits = precision_digits or self.env[
            "decimal.precision"
        ].precision_get("Product Unit of Measure")
        return (
            float_compare(
                self.quantity,
                self.product_uom_qty,
                precision_digits=precision_digits,
            )
            < 0
        )

    def _split_variable_quantity_dest_moves(self, backorder_sources, backorder_moves):
        for source_move, backorder_move in zip(
            backorder_sources, backorder_moves, strict=False
        ):
            if not source_move.picking_type_id.variable_quantity:
                continue
            dest_moves = (
                source_move.move_dest_ids | backorder_move.move_dest_ids
            ).filtered(lambda move: move.state not in {"done", "cancel"})
            if not dest_moves:
                continue
            source_dest_moves, backorder_dest_moves = (
                source_move._get_split_variable_quantity_dest_moves(
                    dest_moves, backorder_move
                )
            )
            source_move.move_dest_ids = [(6, 0, source_dest_moves.ids)]
            backorder_move.move_dest_ids = [(6, 0, backorder_dest_moves.ids)]

    def _get_split_variable_quantity_dest_moves(self, dest_moves, backorder_move):
        source_dest_moves = self.env["stock.move"]
        backorder_dest_moves = self.env["stock.move"]
        qty_left = self.quantity
        rounding = self.product_uom.rounding
        for dest_move in dest_moves.sorted("id"):
            if float_compare(qty_left, 0.0, precision_rounding=rounding) <= 0:
                backorder_dest_moves |= dest_move
                continue
            if (
                float_compare(
                    qty_left,
                    dest_move.product_uom_qty,
                    precision_rounding=rounding,
                )
                >= 0
            ):
                source_dest_moves |= dest_move
                qty_left -= dest_move.product_uom_qty
                continue
            source_dest_moves |= dest_move
            residual_qty = dest_move.product_uom_qty - qty_left
            split_qty = dest_move.product_uom._compute_quantity(
                residual_qty,
                dest_move.product_id.uom_id,
                rounding_method="HALF-UP",
            )
            new_dest_vals = dest_move._split(split_qty)
            for vals in new_dest_vals:
                vals["move_orig_ids"] = [(6, 0, backorder_move.ids)]
            new_dest_moves = self.env["stock.move"].create(new_dest_vals)
            new_dest_moves.with_context(
                bypass_entire_pack=True, bypass_procurement_creation=True
            )._action_confirm(merge=False)
            backorder_dest_moves |= new_dest_moves
            qty_left = 0.0
        return source_dest_moves, backorder_dest_moves

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

# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models
from odoo.tools import float_compare


class StockSplitPicking(models.TransientModel):
    _inherit = "stock.split.picking"

    mode = fields.Selection(
        selection_add=[("kit_quantity", "Quantity of kits")],
        ondelete={"kit_quantity": "set default"},
    )
    kit_split_quantity = fields.Integer(string="Number of kits by transfer")

    def _apply_kit_quantity(self):
        new_pickings = self.env["stock.picking"]
        for picking in self.picking_ids:
            new_moves_vals = []
            moves_to_split_off = self.env["stock.move"]
            # Do not split off moves that are done or cancelled
            todo_qty = self.kit_split_quantity
            todo_moves = picking.move_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            ).sorted()
            todo_moves_by_bom = todo_moves.grouped(lambda m: m.bom_line_id.bom_id)
            # Process each bom
            for bom, moves in todo_moves_by_bom.items():
                # Stop processing if there's nothing else to split off
                if todo_qty <= 0:
                    break
                # Handle kits
                if bom.type == "phantom":
                    kit_quantity = moves._compute_kit_quantities(
                        bom.product_id,
                        bom.product_qty,
                        bom,
                        {
                            "incoming_moves": lambda m: True,
                            "outgoing_moves": lambda m: False,
                        },
                    )
                    # If the kit quantity is lower or equal than the todo_qty, we can
                    # split off the whole kit moves without any move splitting.
                    if (
                        float_compare(
                            kit_quantity,
                            todo_qty,
                            precision_rounding=bom.product_uom_id.rounding,
                        )
                        <= 0
                    ):
                        todo_qty -= kit_quantity
                        moves_to_split_off += moves
                        continue
                    # Otherwise, we'd be consuming the complete todo_qty, but we need to
                    # split the kit component moves.
                    for move in moves:
                        new_moves_vals += move.with_context(
                            cancel_backorder=False
                        )._split(
                            move.product_uom._compute_quantity(
                                move.bom_line_id.product_qty * todo_qty,
                                move.product_id.uom_id,
                                rounding_method="HALF-UP",
                            )
                        )
                    # If we got this far, we've consumed all the todo_qty
                    todo_qty = 0
                    break
                # Handle regular products: use their quantity as they are complete
                else:  # (non-kit)
                    for move in moves:
                        rounding = move.product_uom.rounding
                        # If the move quantity is lower or equal than the todo_qty,
                        # we can split off the whole move without splitting it.
                        if (
                            float_compare(
                                move.product_uom_qty,
                                todo_qty,
                                precision_rounding=rounding,
                            )
                            <= 0
                        ):
                            todo_qty -= move.product_uom_qty
                            moves_to_split_off += move
                            continue
                        # Otherwise, we need to split the move
                        new_moves_vals += move.with_context(
                            cancel_backorder=False
                        )._split(
                            move.product_uom._compute_quantity(
                                todo_qty,
                                move.product_id.uom_id,
                                rounding_method="HALF-UP",
                            )
                        )
                        # If we got this far, we've consumed all the todo_qty
                        todo_qty = 0
                        break
            # Create the partially split off moves
            if new_moves_vals:
                new_moves = self.env["stock.move"].create(new_moves_vals)
                new_moves.with_context(
                    bypass_entire_pack=True, bypass_procurement_creation=True
                )._action_confirm(merge=False)
                moves_to_split_off += new_moves
            # If all the picking moves are the ones to be split, then it means
            # we haven't created any backorder move. We keep the picking as-is.
            if picking.move_ids == moves_to_split_off or not moves_to_split_off:
                continue  # pragma: no cover
            # Create the split orders for the extracted moves, and split them off
            new_pickings += picking._split_off_moves(moves_to_split_off)
        return new_pickings

# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.tools import groupby


class StockSplitPicking(models.TransientModel):
    _inherit = "stock.split.picking"

    mode = fields.Selection(
        selection_add=[("kit_quantity", "Quantity of kits")],
        ondelete={"kit_quantity": "set default"},
    )
    kit_split_quantity = fields.Integer(string="Number of kits by transfer")

    @api.model
    def _sort_move_lines(self, move):
        return move.sequence

    def _apply_kit_quantity(self):
        pickings = self.env["stock.picking"]
        for picking in self.picking_ids:
            pickings |= self._split_by_kit_quantity(picking)
        return self._picking_action(pickings)

    def _split_by_kit_quantity(self, picking):
        filters = {
            "incoming_moves": lambda m: True,
            "outgoing_moves": lambda m: False,
        }
        move_lines = picking.move_lines.filtered(
            lambda m: m.state not in ["done", "cancel"]
        )
        move_lines = move_lines.sorted(self._sort_move_lines)
        moves_to_backorder = self.env["stock.move"]
        new_picking = self.env["stock.picking"]
        used_slots = 0
        max_slots = self.kit_split_quantity
        for bom, bom_move_list in groupby(
            move_lines, key=lambda move: move.bom_line_id.bom_id
        ):

            moves = self.env["stock.move"].browse([move.id for move in bom_move_list])
            if used_slots >= max_slots:
                # Current picking is full, everything else is moved to a new picking
                moves_to_backorder |= moves
                continue

            available_slots = max_slots - used_slots
            if bom.type != "phantom":
                # Non kit moves, their quantity is the number of slots used
                for move in moves:
                    is_reserved = bool(move.move_line_ids)
                    quantity = move.product_qty
                    if available_slots >= quantity:
                        used_slots += quantity
                        available_slots = max_slots - used_slots
                    elif available_slots <= 0:
                        moves_to_backorder |= move
                    else:
                        new_move_vals = move._split(quantity - available_slots)
                        moves_to_backorder |= self.env["stock.move"].create(
                            new_move_vals
                        )
                        if is_reserved:
                            move._action_assign()
                        used_slots = max_slots
            else:
                # Kit moves
                kit_quantity = moves._compute_kit_quantities(
                    bom.product_id,
                    max(moves.mapped("product_qty")),  # Just use max possible
                    bom,
                    filters,
                )
                if kit_quantity <= available_slots:
                    used_slots += kit_quantity
                else:
                    kit_to_split = kit_quantity - available_slots
                    new_move_vals = []
                    is_reserved = bool(moves.move_line_ids)
                    if is_reserved:
                        moves._do_unreserve()
                    for move in moves:
                        new_move_vals += move._split(
                            move.bom_line_id.product_qty * kit_to_split
                        )
                    moves_to_backorder |= self.env["stock.move"].create(new_move_vals)
                    if is_reserved:
                        moves._action_assign()
                    used_slots = max_slots
        if moves_to_backorder:
            new_picking = picking._create_split_backorder()
            moves_to_backorder.write({"picking_id": new_picking.id})
            moves_to_backorder.move_line_ids.write({"picking_id": new_picking.id})

        return new_picking

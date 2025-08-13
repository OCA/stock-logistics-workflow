# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class StockSplitPicking(models.TransientModel):
    _name = "stock.split.picking"
    _description = "Split a picking"

    mode = fields.Selection(
        [
            ("quantity", "Quantities"),
            ("move", "One picking per move"),
            ("selection", "Select move lines to split off"),
        ],
        required=True,
        default="quantity",
    )

    picking_ids = fields.Many2many(
        "stock.picking",
        default=lambda self: self._default_picking_ids(),
    )
    move_ids = fields.Many2many("stock.move")

    def _default_picking_ids(self):
        return self.env["stock.picking"].browse(self.env.context.get("active_ids", []))

    def action_apply(self):
        new_pickings = getattr(self, f"_apply_{self[:1].mode}")()
        return self._picking_action(new_pickings)

    def _check_can_split_by_quantity(self):
        for picking in self.picking_ids:
            if all(
                float_is_zero(m.quantity, precision_rounding=m.product_uom.rounding)
                for m in picking.move_ids
            ):
                raise UserError(
                    self.env._(
                        "%s: Nothing to split. Fill the quantities you want in a new "
                        "transfer in the done quantities",
                        picking.display_name,
                    )
                )
            if all(
                float_compare(
                    m.quantity,
                    m.product_uom_qty,
                    precision_rounding=m.product_uom.rounding,
                )
                >= 0
                for m in picking.move_ids
            ):
                raise UserError(
                    self.env._(
                        "%s: Nothing to split, all demand is done. For split you need "
                        "at least one line not fully fulfilled",
                        picking.display_name,
                    )
                )

    def _apply_quantity(self):
        """Apply mode `quantity`: Split pickings by quantity

        Done quantities will be moved to a new picking, the remaining pending
        moves will stay in the original picking.

        This is similar to the core method `action_split_transfer`, with one important
        difference: the core method keeps the assigned quantities in the original record
        and creates a backorder for the remaining quantities. This method, on the other
        hand, extracts the selected quantities in a new picking, and keeps the original
        one as backorder.
        """
        self._check_can_split_by_quantity()
        new_pickings = self.env["stock.picking"]
        for picking in self.picking_ids:
            new_moves_vals = []
            moves_to_split_off = self.env["stock.move"]
            moves_to_recompute_state = self.env["stock.move"]
            for move in picking.move_ids:
                rounding = move.product_uom.rounding
                # Do not split moves that are done or cancelled
                if move.state in ("done", "cancel"):
                    continue
                # If there aren't assigned quantities, there's nothing to split
                if float_is_zero(move.quantity, precision_rounding=rounding):
                    continue
                # If it's completely assigned, extract the move entirely
                if (
                    float_compare(
                        move.quantity, move.product_uom_qty, precision_rounding=rounding
                    )
                    >= 0
                ):
                    moves_to_split_off += move
                    continue
                # Otherwise, we split the done quantities and leave the remaining
                # quantities in the original move.
                split_moves_vals = move.with_context(cancel_backorder=False)._split(
                    move.product_uom._compute_quantity(
                        move.quantity, move.product_id.uom_id, rounding_method="HALF-UP"
                    )
                )
                if not split_moves_vals:
                    continue  # pragma: no cover
                # Adopt the move lines from the original move
                split_moves_vals[0]["move_line_ids"] = [
                    Command.set(move.move_line_ids.ids)
                ]
                new_moves_vals += split_moves_vals
                moves_to_recompute_state += move
            # Create the partially split off moves
            if new_moves_vals:
                new_moves = self.env["stock.move"].create(new_moves_vals)
                new_moves.with_context(
                    bypass_entire_pack=True, bypass_procurement_creation=True
                )._action_confirm(merge=False)
                moves_to_split_off += new_moves
            # Recompute the state of the remaining moves
            moves_to_recompute_state._recompute_state()
            # If all the picking moves are the ones to be split, then it means
            # we haven't created any backorder move. We keep the picking as-is.
            if picking.move_ids == moves_to_split_off or not moves_to_split_off:
                continue  # pragma: no cover
            # Create the split orders for the extracted moves, and split them off
            new_pickings += picking._split_off_moves(moves_to_split_off)
        return new_pickings

    def _apply_move(self):
        """Apply mode `mode`: One picking per move

        Extract the first move from the picking and move it to a new one.
        Keep the rest in the original picking.
        """
        new_pickings = self.env["stock.picking"]
        for picking in self.picking_ids:
            # If the picking only has one move, there's nothing to split
            if len(picking.move_ids) <= 1:
                continue
            # Get the moves that can be split off (not done nor cancelled)
            todo = picking.move_ids.filtered(
                lambda move: move.state not in ("done", "cancel")
            ).sorted()
            if not todo:
                continue
            # Split off the first one
            new_pickings += picking._split_off_moves(todo[0])
        return new_pickings

    def _apply_selection(self):
        """Apply mode `selection`: Split off selected moves"""
        moves = self.mapped("move_ids")
        new_picking = moves.mapped("picking_id")._split_off_moves(moves)
        return new_picking

    def _picking_action(self, pickings):
        if not pickings:
            return True
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all",
        )
        action["domain"] = [("id", "in", pickings.ids)]
        return action

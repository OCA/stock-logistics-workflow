# Copyright 2013-2015 Camptocamp SA - Nicolas Bessi
# Copyright 2018 Camptocamp SA - Julien Coux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    def _check_split_process(self):
        # Check the picking state and condition before split
        if self.state == "draft":
            raise UserError(_("Mark as todo this picking please."))
        if all([x.qty_done == 0.0 for x in self.move_line_ids]):
            raise UserError(
                _(
                    "You must enter done quantity in order to split your "
                    "picking in several ones."
                )
            )

    def split_process(self):
        """Use to trigger the wizard from button with correct context"""
        for picking in self:
            picking._check_split_process()

            # Split moves considering the qty_done on moves
            new_moves = self.env["stock.move"]
            new_move_lines = self.env["stock.move.line"]
            for move in picking.move_ids:
                if move.quantity_done:
                    qty_uom_split = move.product_uom._compute_quantity(
                        move.quantity_done, move.product_id.uom_id, rounding_method="HALF-UP"
                    )
                    # Empty list is returned for moves with zero qty_done.
                    new_move_vals = move.with_context(cancel_backorder=False)._split(
                        qty_uom_split
                    )
                    if new_move_vals:
                        new_move_line_vals = []
                        for move_line in move.move_line_ids:
                            if move_line.reserved_qty and move_line.qty_done:
                                new_move_line_vals += move_line._split(move_line.qty_done)

                        # Create new move and move lines
                        new_move = self.env["stock.move"].create(new_move_vals)
                        for vals in new_move_line_vals:
                            vals['move_id'] = new_move.id
                        new_move_lines |= self.env["stock.move.line"].create(new_move_line_vals)
                    else:
                        new_move = move
                    new_move._action_confirm(merge=False)
                    new_moves |= new_move

            # If we have new moves to move, create the backorder picking
            if new_moves:
                backorder_picking = picking._create_split_backorder()
                new_moves.write({"picking_id": backorder_picking.id})
                if new_move_lines:
                    new_move_lines.write({"picking_id": backorder_picking.id})
                    new_moves._recompute_state()
                else:
                    new_moves._action_assign()
                return backorder_picking

    def _create_split_backorder(self, default=None):
        """Copy current picking with defaults passed, post message about
        backorder"""
        self.ensure_one()
        backorder_picking = self.copy(
            dict(
                {
                    "name": "/",
                    "move_ids": [],
                    "move_line_ids": [],
                    "backorder_id": self.id,
                },
                **(default or {})
            )
        )
        self.message_post(
            body=_(
                "The backorder %s has been created.", backorder_picking._get_html_link()
            )
        )
        return backorder_picking

    def _split_off_moves(self, moves):
        """Remove moves from pickings in self and put them into a new one"""
        new_picking = self.env["stock.picking"]
        for this in self:
            if this.state in ("done", "cancel"):
                raise UserError(
                    _("Cannot split picking {name} in state {state}").format(
                        name=this.name, state=this.state
                    )
                )
            new_picking = new_picking or this._create_split_backorder()
            if not this.move_ids - moves:
                raise UserError(
                    _("Cannot split off all moves from picking %s") % this.name
                )
        moves.write({"picking_id": new_picking.id})
        moves.mapped("move_line_ids").write({"picking_id": new_picking.id})
        return new_picking

# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockSplitPicking(models.TransientModel):
    _name = "stock.split.picking"
    _description = "Split a picking"

    mode = fields.Selection(
        [
            ("done", "Done quantities"),
            ("move", "One picking per move"),
            (
                "available_line",
                "Split move lines between available and not available move lines",
            ),
            (
                "available_product",
                "Split move lines between available and not available products",
            ),
            ("selection", "Select move lines to split off"),
        ],
        required=True,
        default="done",
    )

    picking_ids = fields.Many2many(
        "stock.picking",
        default=lambda self: self._default_picking_ids(),
    )
    move_ids = fields.Many2many("stock.move")

    def _default_picking_ids(self):
        return self.env["stock.picking"].browse(self.env.context.get("active_ids", []))

    def action_apply(self):
        return getattr(self, "_apply_%s" % self[:1].mode)()

    def _apply_done(self):
        return self.picking_ids.split_process("quantity_done")

    def _apply_move(self):
        """Create new pickings for every move line, keep first
        move line in original picking
        """
        new_pickings = self.env["stock.picking"]
        for picking in self.picking_ids:
            for move in picking.move_lines[1:]:
                new_pickings += picking._split_off_moves(move)
        return self._picking_action(new_pickings)

    def _apply_available_line(self):
        """Create different pickings for available and not available move line"""
        for picking in self.picking_ids:
            moves = picking.move_lines
            moves_available = moves.filtered(lambda move: move.state == "assigned")
            moves_available.picking_id._split_off_moves(moves_available)
        return self._picking_action(self.picking_ids)

    def _apply_available_product(self):
        """Create different pickings for available and not available move line"""
        return self.picking_ids.split_process("reserved_availability")

    def _apply_selection(self):
        """Create one picking for all selected moves"""
        moves = self.move_ids
        new_picking = moves.picking_id._split_off_moves(moves)
        return self._picking_action(new_picking)

    def _picking_action(self, pickings):
        return pickings.get_formview_action() if pickings else False

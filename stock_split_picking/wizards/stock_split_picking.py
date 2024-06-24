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
            for move in picking.move_ids[1:]:
                new_pickings += picking._split_off_moves(move)
        return self._picking_action(new_pickings)

    def _apply_available_line(self):
        """Create different pickings for available and not available move line"""
        for picking in self.picking_ids:
            moves_available = picking.move_ids.filtered(
                lambda move: move.state == "assigned"
            )
            new_picking = moves_available.picking_id._split_off_moves(moves_available)
        return self._picking_action(new_picking)

    def _apply_available_product(self):
        """Create different pickings for available and not available move line"""
        self.picking_ids.split_process("reserved_availability")
        self.picking_ids.move_ids._recompute_state()
        return True
        

    def _apply_selection(self):
        """Create one picking for all selected moves"""
        moves = self.move_ids
        new_picking = moves.picking_id._split_off_moves(moves)
        return self._picking_action(new_picking)

    def _picking_action(self, pickings):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all",
        )
        action["domain"] = [("id", "in", pickings.ids)]
        return action if pickings else False

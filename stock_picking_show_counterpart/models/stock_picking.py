from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    related_picking_count = fields.Integer(compute="_compute_related_picking_count")

    def _get_related_pickings(self):
        """New method to return pickings related by move origins or destinations."""
        self.ensure_one()
        moves = self.move_ids
        related_moves = moves.mapped(
            lambda move: move.move_dest_ids | move.move_orig_ids
        )
        return related_moves.mapped("picking_id") - self

    @api.depends("move_ids.move_dest_ids", "move_ids.move_orig_ids")
    def _compute_related_picking_count(self):
        """New method to compute the number of related pickings."""
        for picking in self:
            picking.related_picking_count = len(picking._get_related_pickings())

    def _get_action_view_picking(self, pickings):
        """New method to return a tree/form view for the given pickings."""
        action = {
            "type": "ir.actions.act_window",
            "name": "Related Pickings",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("id", "in", pickings.ids)],
        }
        if len(pickings) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": pickings.id,
                }
            )
        return action

    def action_view_related_pickings(self):
        """New method to open related pickings in tree/form view."""
        self.ensure_one()
        related_pickings = self._get_related_pickings()
        return self._get_action_view_picking(related_pickings)

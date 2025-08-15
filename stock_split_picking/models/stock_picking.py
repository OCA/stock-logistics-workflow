# Copyright 2013-2015 Camptocamp SA - Nicolas Bessi
# Copyright 2018 Camptocamp SA - Julien Coux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from ..exceptions import NotPossibleToSplitPickError, SplitPickNotAllowedInStateError


class StockPicking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    def _create_split_order(self, default=None):
        """Create the split order for the extracted moves"""
        self.ensure_one()
        split_picking = self.copy(
            dict(
                {
                    "name": "/",
                    "move_ids": [],
                    "move_line_ids": [],
                },
                **(default or {}),
            )
        )
        self.message_post(
            body=self.env._(
                "The split order %s has been created.", split_picking._get_html_link()
            )
        )
        split_picking.message_post(
            body=self.env._("Split off from %s", self._get_html_link())
        )
        return split_picking

    def _split_off_moves(self, moves):
        """Remove moves from pickings in self and put them into a new one

        :return: The new picking created for the split off moves
        """
        new_picking = self.env["stock.picking"]
        for picking in self:
            if picking.state in ("done", "cancel"):
                raise SplitPickNotAllowedInStateError(self.env, picking)
            new_picking = new_picking or picking._create_split_order()
            if not picking.move_ids - moves:
                raise NotPossibleToSplitPickError(self.env, picking)
        moves.write({"picking_id": new_picking.id})
        moves.mapped("move_line_ids").write({"picking_id": new_picking.id})
        if picking.state in ("confirmed", "waiting", "assigned"):
            new_picking.move_ids._action_confirm(merge=False)
        return new_picking

# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


def get_first_move_dest(moves, done=False):
    move_states = ("cancel", "done")
    for move in moves.move_dest_ids:
        if move.state in move_states if done else move.state not in move_states:
            return move


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ship_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        compute="_compute_ship_picking_data",
        string="Related delivery",
    )
    ship_carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        compute="_compute_ship_picking_data",
        string="Related carrier",
    )

    def _compute_ship_picking_data(self):
        for picking in self:
            ship = picking._get_ship_from_chain()
            picking.ship_picking_id = ship
            picking.ship_carrier_id = ship.carrier_id

    def _get_ship_from_chain(self, done=False):
        """Returns the shipment related to the current operation."""
        move_dest = get_first_move_dest(self.move_lines, done=done)
        while move_dest:
            picking = move_dest.picking_id
            if picking.picking_type_id.code == "outgoing":
                return picking
            move_dest = get_first_move_dest(move_dest, done=done)
        # Should return an empty record if we reach this line
        return self.browse()

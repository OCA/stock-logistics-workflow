# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def _propagate_procurement_group(self, group):
        """Write group to self and propagate group to dest moves where
        propagate is True.
        Reassign picking to ensure no moves with different group share the
        same picking.
        Goal is to have all linked destination moves sharing the same
        procurement group all along the chain.
        """
        # Write the group and assign new picking
        res = self.write({'group_id': group.id, 'picking_id': False})
        self._assign_picking()
        # If there are destination move to propagate, propagate proc group
        to_propagate = self.filtered(
            lambda m: m.move_dest_ids and m.propagate
        ).mapped('move_dest_ids').filtered(lambda m: not m.group_id)
        if to_propagate:
            # Recursive call on destination moves
            to_propagate._propagate_procurement_group(group)
        return res

    @api.multi
    def _propagate_quantity_to_dest_moves(self):
        """Propagate the quantity to all dest moves where propagate is True."""
        for move in self.filtered(lambda m: m.propagate):
            for dest_move in move.move_dest_ids:
                # Convert qty in dest move uom if needed
                if move.product_uom != dest_move.product_uom:
                    new_qty = move.product_uom._compute_quantity(
                        move.product_uom_qty, dest_move.product_uom)
                else:
                    new_qty = move.product_uom_qty
                dest_move.write({
                    'product_uom_qty': new_qty
                })
                # Recursive call on destination moves
                dest_move._propagate_quantity_to_dest_moves()
        return True

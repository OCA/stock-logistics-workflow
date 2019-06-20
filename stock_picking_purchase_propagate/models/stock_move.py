# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def get_next_moves_to_propagate(self):
        """Get the destination moves of self, if self is to propagate and no
        group_id is defined on the dest moves."""
        sql = """
            SELECT dest_mov.id
            FROM stock_move dest_mov
            INNER JOIN stock_move_move_rel rel
                ON rel.move_dest_id = dest_mov.id
            INNER JOIN stock_move orig_mov ON rel.move_orig_id = orig_mov.id
            WHERE orig_mov.propagate = TRUE
            AND dest_mov.group_id IS NULL
            AND orig_mov.id IN %s;
            """
        self.env.cr.execute(sql, [tuple(self.ids)])
        dest_moves_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.browse(dest_moves_ids)

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
        to_propagate = self.get_next_moves_to_propagate()
        if to_propagate:
            # Recursive call on destination moves
            to_propagate._propagate_procurement_group(group)
        return res

    @api.multi
    def _propagate_quantity_to_dest_moves(self):
        """Propagate the quantity if propagate and only one dest move."""
        for move in self:
            if not move.propagate:
                continue
            dest_move = move.move_dest_ids
            # Stop propagation of qty if multiple dest moves
            if len(dest_move) != 1:
                continue
            # If there's only one dest move, there's no risk to propagate
            # Convert qty in dest move uom if needed
            if move.product_uom != dest_move.product_uom:
                dest_qty = move.product_uom._compute_quantity(
                    move.product_uom_qty, dest_move.product_uom)
            else:
                dest_qty = move.product_uom_qty
            dest_move.write({
                'product_uom_qty': dest_qty
            })
            # Recursive call on destination moves
            dest_move._propagate_quantity_to_dest_moves()
        return True

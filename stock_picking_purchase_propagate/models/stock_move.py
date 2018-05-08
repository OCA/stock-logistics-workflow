# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def _propagate_procurement_group(self, group, force=False):
        """Propagate the proc. group to all dest moves where propagate is True.

        Goal is to have all moves related to a same PO with the same PG all
        along the chain, even if the PO has been generated from an OP.
        """
        res = self.write({'group_id': group.id, 'picking_id': False})
        self._assign_picking()
        to_propagate = self.filtered(
            lambda m: m.move_dest_ids and m.propagate
        ).mapped('move_dest_ids')
        if to_propagate:
            if not force:
                to_propagate = to_propagate.filtered(lambda m: not m.group_id)
            to_propagate._propagate_procurement_group(group)
        return res

    @api.multi
    def _propagate_quantity(self):
        """Propagate the quantity to all dest moves where propagate is True"""
        for move in self:
            for dest_move in move.move_dest_ids.filtered(
                    lambda m: m.propagate):
                new_qty = move.product_uom._compute_quantity(
                    move.product_uom_qty, dest_move.product_uom)
                dest_move.write({
                    'product_uom_qty': new_qty
                })
                dest_move._propagate_quantity()
        return True

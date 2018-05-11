# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.multi
    def _create_stock_moves(self, picking):
        """ When creating the moves from a PO, propagate the procurement group
            and quantity from the PO lines to the destination moves, and
            reassign pickings.
        """
        moves = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        destination_moves_to_prop = moves.filtered(
            lambda m: m.propagate).mapped('move_dest_ids').filtered(
            lambda m: not m.group_id)
        destination_moves_to_prop._propagate_procurement_group(
            moves.mapped('group_id'))
        moves._propagate_quantity_to_dest_moves()
        return moves

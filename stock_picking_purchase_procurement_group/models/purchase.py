# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.multi
    def _create_stock_moves(self, picking):
        """ When creating the moves from a PO, propagate the procurement group
            to following chain and ensure the existing move (in case of OP)
            belong to a separate picking per PO.
        """
        res = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for move in res:
            move._propagate_procurement_group(move.group_id)
        return res

# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def _propagate_procurement_group(self, group, force=False):
        """Propagate the proc. group to all dest moves if propagate is True.

        Goal is to have all moves related to a same PO in a same picking all
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

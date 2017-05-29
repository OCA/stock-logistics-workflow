# -*- coding: utf-8 -*-
# © 2015 Leonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api

from collections import defaultdict


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _prepare_pack_ops(self, quants, forced_qties):
        """Get the owner from the moves instead of the picking.

        The only case we need to fix is the one of receptions. In that case, we
        do not receive any quants (because there is no quant reservation). We
        group the moves by product and owner, and run the original method
        separately for each one.

        """

        if quants:
            return super(Picking, self)._prepare_pack_ops(quants, forced_qties)

        grouped = defaultdict(list)
        ops_data = []

        for move in self.move_lines:
            if move.state not in ('assigned', 'confirmed'):
                continue
            grouped[(move.product_id, move.restrict_partner_id)].append(move)

        for product, owner in grouped:
            qty = sum(m.product_qty for m in grouped[(product, owner)])
            op_data = super(Picking, self)._prepare_pack_ops(quants,
                                                             {product: qty})
            for x in op_data:
                x['owner_id'] = owner.id

            ops_data += op_data

        return ops_data

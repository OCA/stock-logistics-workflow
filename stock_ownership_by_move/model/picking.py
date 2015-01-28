# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp import models, api

from collections import defaultdict


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):
        """Get the owner from the moves instead of the picking.

        The only case we need to fix is the one of receptions. In that case, we
        do not receive any quants (because there is no quant reservation). We
        group the moves by product and owner, and run the original method
        separately for each one.

        """

        if quants:
            return super(Picking, self)._prepare_pack_ops(picking, quants,
                                                          forced_qties)

        grouped = defaultdict(list)
        ops_data = []

        for move in picking.move_lines:
            grouped[(move.product_id, move.restrict_partner_id)].append(move)

        for product, owner in grouped:
            qty = sum(m.product_qty for m in grouped[(product, owner)])
            op_data = super(Picking, self)._prepare_pack_ops(picking, quants,
                                                             {product: qty})
            for x in op_data:
                x['owner_id'] = owner.id

            ops_data += op_data

        return ops_data

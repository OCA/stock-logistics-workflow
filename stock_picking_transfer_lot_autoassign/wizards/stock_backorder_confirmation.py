# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.multi
    def process_assign_ordered_qty(self):
        """Autocomplete product qty with producto ordered qty only for
        products without lots track
        """
        self.ensure_one()
        for pack_operation in self.pick_id.pack_operation_ids:
            if pack_operation.pack_lot_ids:
                continue
            pack_operation.qty_done = pack_operation.product_qty
        self._process()

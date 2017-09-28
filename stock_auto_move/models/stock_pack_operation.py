# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockPackOperation(models.Model):

    _inherit = 'stock.pack.operation'

    @api.multi
    def _auto_fill_pack_lot_ids_qty(self):
        """
        This method automatically fills quantites of the lots
        used in operations and also update the qty done on
        those operations.
        This method is meant to be used with automatic moves.
        """
        operations = self.filtered(
            lambda o: o.pack_lot_ids and o.product_id and
            not o.package_id and not o.result_package_id)
        for operation in operations:
            for pack_lot in operations.mapped('pack_lot_ids'):
                if not pack_lot.qty:
                    pack_lot.qty = pack_lot.qty_todo
            operation.qty_done = operation.product_qty
        return True

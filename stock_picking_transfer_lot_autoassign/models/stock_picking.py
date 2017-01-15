# -*- coding: utf-8 -*-
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):
        """Auto-assign as done the quantity proposed for the lots"""
        res = super(StockPicking, self)._prepare_pack_ops(
            picking, quants, forced_qties,
        )
        for pack_op_vals in res:
            qty_done = 0
            for pack_lot_vals in pack_op_vals.get('pack_lot_ids', []):
                pack_lot_vals[2]['qty'] = pack_lot_vals[2]['qty_todo']
                qty_done += pack_lot_vals[2]['qty_todo']
            if qty_done:
                pack_op_vals['qty_done'] = qty_done
        return res

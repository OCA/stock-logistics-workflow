# -*- coding: utf-8 -*-
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _prepare_pack_ops(self, quants, forced_qties):
        """Auto-assign as done the quantity proposed for the lots"""
        self.ensure_one()
        res = super(StockPicking, self)._prepare_pack_ops(
            quants, forced_qties,
        )
        if self.picking_type_id.avoid_internal_assignment:
            return res
        for pack_op_vals in res:
            qty_done = 0
            for pack_lot_vals in pack_op_vals.get('pack_lot_ids', []):
                pack_lot_vals[2]['qty'] = pack_lot_vals[2]['qty_todo']
                qty_done += pack_lot_vals[2]['qty_todo']
            if qty_done:
                pack_op_vals['qty_done'] = qty_done
        return res

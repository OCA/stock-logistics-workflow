# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """Auto-assign as done the quantity proposed for the lots"""
        self.ensure_one()
        res = super()._prepare_move_line_vals(quantity, reserved_quant)
        if not self.picking_id.auto_fill_operation:
            return res
        elif self.picking_id.picking_type_id.avoid_lot_assignment and res.get("lot_id"):
            return res
        res.update({"qty_done": res.get("product_uom_qty", 0.0)})
        return res

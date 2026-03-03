# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_picked_quantity(self):
        if self._ml_has_qty_picked():
            return self._sum_ml_qty_picked()
        return super()._get_picked_quantity()

    def _ml_has_qty_picked(self):
        return self.picked and any(ml.qty_picked for ml in self.move_line_ids)

    def _sum_ml_qty_picked(self):
        self.ensure_one()
        quantity = 0
        for move_line in self.move_line_ids.filtered("picked"):
            quantity += move_line.product_uom_id._compute_quantity(
                move_line.qty_picked, self.product_uom, round=False
            )
        return quantity

    def _action_done(self, cancel_backorder=False):
        for move in self:
            for line in move.move_line_ids:
                if line.picked and float_compare(
                    line.qty_picked,
                    line.quantity,
                    precision_rounding=line.product_uom_id.rounding,
                ):
                    line.quantity = line.qty_picked
        return super()._action_done(cancel_backorder=cancel_backorder)

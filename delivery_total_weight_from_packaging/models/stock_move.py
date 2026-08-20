# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _cal_move_weight(self):
        # Override method from `stock_delivery` module to compute a more accurate
        # weight from the product packaging.
        for move in self:
            move.weight = move.product_id.get_total_weight_from_packaging(
                move.product_qty
            )

    def _get_processible_quantity(self):
        self.ensure_one()
        if self.product_id:
            return self.quantity
        return 0

    def _get_estimated_weight(self):
        self.ensure_one()
        product = self.product_id
        if product:
            quantity = self._get_processible_quantity()
            return product.get_total_weight_from_packaging(quantity)
        return 0

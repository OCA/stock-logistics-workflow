# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def _create_correction_svl(self, move, diff):
        if move.product_id.cost_method != "average" or self.env.context.get(
            "new_stock_move_create", False
        ):
            return super()._create_correction_svl(move, diff)
        for svl in move.stock_valuation_layer_ids:
            # TODO: Review if is dropshipping
            if move._is_out():
                svl.quantity -= diff
            else:
                svl.quantity += diff

    @api.model_create_multi
    def create(self, vals_list):
        return super(
            StockMoveLine, self.with_context(new_stock_move_create=True)
        ).create(vals_list)

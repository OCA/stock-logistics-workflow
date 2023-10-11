# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockValuationLayer(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        """Transfer changes to the production movement to execute the synchronisation."""
        res = super().write(vals)
        for move in self:
            if (
                "price_unit" in vals
                and move.is_subcontract
                and not self.env.context.get("skip_stock_price_unit_sync")
            ):
                orig_moves = move.move_orig_ids
                orig_moves.write({"price_unit": vals["price_unit"]})
                svls = orig_moves.sudo().mapped("stock_valuation_layer_ids")
                svls.write({"unit_cost": vals["price_unit"]})
        return res

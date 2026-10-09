# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
    ):
        move_values = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
        )
        quant = values.get("quant_lock_quant_id")
        if quant:
            # The rule source location may be a parent of the quant location:
            # the lock move must start from the exact quant location to
            # reserve it.
            move_values.update(
                {
                    "location_id": quant.location_id.id,
                    "quant_lock_quant_id": quant.id,
                }
            )
        return move_values

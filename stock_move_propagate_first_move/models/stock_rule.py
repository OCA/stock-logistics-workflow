# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):

    _inherit = "stock.rule"

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        stock_move_values = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        move_dest = values.get("move_dest_ids")
        if move_dest:
            stock_move_values["first_move_id"] = (
                move_dest[0].first_move_id.id
                if move_dest[0].first_move_id
                else move_dest[0].id
            )
        return stock_move_values

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        values = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        if move_to_copy.first_move_id:
            first_move = move_to_copy.first_move_id
        else:
            first_move = move_to_copy
        values["first_move_id"] = first_move.id
        return values

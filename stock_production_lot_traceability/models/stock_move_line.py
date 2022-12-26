# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        # OVERRIDE to invalidate the cache of the lots' produce/consume fields,
        # as they're computed from the move lines that consume/produce them.
        self.env["stock.production.lot"].invalidate_cache(
            [
                "produce_lot_ids",
                "consume_lot_ids",
                "produce_lot_count",
                "consume_lot_count",
            ]
        )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE to invalidate the cache of the lots' produce/consume fields,
        # as they're computed from the move lines that consume/produce them.
        self.env["stock.production.lot"].invalidate_cache(
            [
                "produce_lot_ids",
                "consume_lot_ids",
                "produce_lot_count",
                "consume_lot_count",
            ]
        )
        return super().create(vals_list)

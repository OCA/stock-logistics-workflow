# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if (
            self.product_id.detailed_type == "consu"
            and self.location_id.usage == "internal"
        ):
            putaway_loc = self.location_id._get_putaway_strategy(self.product_id)
            res["location_id"] = putaway_loc.id
        return res

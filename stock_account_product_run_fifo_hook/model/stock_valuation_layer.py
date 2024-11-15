# Copyright 2024 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model_create_multi
    def create(self, values):
        if any("taken_data" in val.keys() for val in values):
            taken_data = [
                "taken_data" in val.keys() and val.pop("taken_data") or {}
                for val in values
            ]
            return super(
                StockValuationLayer, self.with_context(taken_data=taken_data)
            ).create(values)
        else:
            return super().create(values)

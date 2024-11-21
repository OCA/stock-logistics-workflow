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

    def _fifo_new_get_value_taken_on_candidate(
        self, qty_taken_on_candidate, candidate_unit_cost
    ):
        value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
        value_taken_on_candidate = self.currency_id.round(value_taken_on_candidate)
        return value_taken_on_candidate

    def _fifo_vacuum_get_value_taken_on_candidate(
        self, qty_taken_on_candidate, candidate_unit_cost
    ):
        value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
        value_taken_on_candidate = self.currency_id.round(value_taken_on_candidate)
        return value_taken_on_candidate

    def _fifo_vacuum_get_corrected_value(self, corrected_value):
        corrected_value = self.currency_id.round(corrected_value)
        return corrected_value

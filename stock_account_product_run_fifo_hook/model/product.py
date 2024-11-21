# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_prepare_candidate_update(
        self,
        candidate,
        qty_taken_on_candidate,
        value_taken_on_candidate,
        candidate_vals,
    ):
        return candidate_vals

    def _run_fifo_vacuum_prepare_candidate_update(
        self,
        svl_to_vacuum,
        candidate,
        qty_taken_on_candidate,
        value_taken_on_candidate,
        candidate_vals,
    ):
        return candidate_vals

    def _get_candidates_domain(self, company):
        return self._get_fifo_candidates_domain(company)

    def _price_updateable(self, new_standard_price=False):
        return new_standard_price and self.cost_method == "fifo"

    def _get_rounded_value(self, quantity, currency):
        return (currency.round(quantity * self.standard_price),)

    def _get_rounded_error(self, currency, quantity):
        return currency.round(
            (self.standard_price * self.quantity_svl - self.value_svl)
            * abs(quantity / self.quantity_svl)
        )

    def _get_change_price_diff_value(
        self, company_id, rounded_new_price, quantity_svl, value_svl
    ):
        return company_id.currency_id.round(
            (rounded_new_price * quantity_svl) - value_svl
        )

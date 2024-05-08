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
        candidates_domain = [
            ("product_id", "=", self.id),
            ("remaining_qty", ">", 0),
            ("company_id", "=", company.id),
        ]
        return candidates_domain

    def _price_updateable(self, new_standard_price=False):
        return new_standard_price and self.cost_method == "fifo"

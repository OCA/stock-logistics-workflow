# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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
        candidate_vals = super(ProductProduct, self)._run_fifo_prepare_candidate_update(
            candidate, qty_taken_on_candidate, value_taken_on_candidate, candidate_vals
        )
        move_id = self.env.context.get("used_in_move_id", False)
        self.env["stock.valuation.layer.usage"].sudo().create(
            {
                "stock_valuation_layer_id": candidate.id,
                "stock_move_id": move_id,
                "quantity": qty_taken_on_candidate,
                "value": value_taken_on_candidate,
                "company_id": candidate.company_id.id,
            }
        )
        return candidate_vals

    def _run_fifo_vacuum_prepare_candidate_update(
        self,
        svl_to_vacuum,
        candidate,
        qty_taken_on_candidate,
        value_taken_on_candidate,
        candidate_vals,
    ):
        candidate_vals = super(
            ProductProduct, self
        )._run_fifo_vacuum_prepare_candidate_update(
            svl_to_vacuum,
            candidate,
            qty_taken_on_candidate,
            value_taken_on_candidate,
            candidate_vals,
        )
        move_id = (
            svl_to_vacuum.stock_move_id and svl_to_vacuum.stock_move_id.id or False
        )
        if svl_to_vacuum:
            self.env["stock.valuation.layer.usage"].sudo().create(
                {
                    "stock_valuation_layer_id": candidate.id,
                    "stock_move_id": move_id,
                    "quantity": qty_taken_on_candidate,
                    "value": value_taken_on_candidate,
                    "company_id": candidate.company_id.id,
                }
            )
        return candidate_vals

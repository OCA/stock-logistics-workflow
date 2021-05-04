# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.osv import expression


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

    def _get_candidates(self, company):
        res = super()._get_candidates(company)
        reserved_from = self.env.context.get("reserved_from", False)
        # Here we try to not pick layers reserved for an MTO scenario
        if reserved_from:
            # Case 1: the layer out has reserved an incoming move,
            # we search amount those
            res = res.filtered(lambda svl: svl.stock_move_id.id in reserved_from)
        else:
            # Case 2: the layer out did not reserve any move,
            # we pick the oldest among the ones not reserved for any
            res = res.filtered(lambda svl: not svl.stock_move_id.move_dest_ids)
        return res

    def _get_candidates_domain(self, company):
        res = super()._get_candidates_domain(company)
        reserved_from = self.env.context.get("reserved_from", False)
        if reserved_from:
            # Case 1: the layer out has reserved an incoming move,
            # we search amount those
            res = expression.AND([res, [("stock_move_id", "in", reserved_from)]])
        else:
            # Case 2: the layer out did not reserve any move,
            # we pick the oldest among the ones not reserved for any
            res = expression.AND([res, [("stock_move_id.move_dest_ids", "=", False)]])
        return res

# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_is_zero


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_fifo_candidates_domain(self, company):
        res = super()._get_fifo_candidates_domain(company)
        fifo_lot = self.env.context.get("fifo_lot")
        if not fifo_lot:
            return res
        return expression.AND([res, [("lot_ids", "in", fifo_lot.ids)]])

    def _sort_by_all_candidates(self, all_candidates, sort_by):
        """Hook function for other sort by"""
        return all_candidates

    def _get_fifo_candidates(self, company):
        all_candidates = super()._get_fifo_candidates(company)
        fifo_lot = self.env.context.get("fifo_lot")
        if fifo_lot:
            for svl in all_candidates:
                if not svl._get_unconsumed_in_move_line(fifo_lot):
                    all_candidates -= svl
            if not all_candidates:
                raise UserError(
                    _(
                        "There is no remaining balance for FIFO valuation for the "
                        "lot/serial %s. Please select a Force FIFO Lot/Serial in the "
                        "detailed operation line."
                    )
                    % fifo_lot.display_name
                )
        sort_by = self.env.context.get("sort_by")
        if sort_by == "lot_create_date":

            def sorting_key(candidate):
                if candidate.lot_ids:
                    return min(candidate.lot_ids.mapped("create_date"))
                return candidate.create_date

            all_candidates = all_candidates.sorted(key=sorting_key)
        elif sort_by is not None:
            all_candidates = self._sort_by_all_candidates(all_candidates, sort_by)
        return all_candidates

    # Depends on https://github.com/odoo/odoo/pull/180245
    def _get_qty_taken_on_candidate(self, qty_to_take_on_candidates, candidate):
        fifo_lot = self.env.context.get("fifo_lot")
        if fifo_lot:
            candidate_ml = candidate._get_unconsumed_in_move_line(fifo_lot)
            qty_to_take_on_candidates = min(
                qty_to_take_on_candidates, candidate_ml.qty_remaining
            )
            candidate_ml.qty_consumed += qty_to_take_on_candidates
            candidate_ml.value_consumed += qty_to_take_on_candidates * (
                candidate.remaining_value / candidate.remaining_qty
            )
        return super()._get_qty_taken_on_candidate(qty_to_take_on_candidates, candidate)

    def _run_fifo(self, quantity, company):
        self.ensure_one()
        fifo_move = self._context.get("fifo_move")
        if self.tracking == "none" or not fifo_move:
            return super()._run_fifo(quantity, company)
        remaining_qty = quantity
        vals = defaultdict(float)
        correction_ml = self.env.context.get("correction_move_line")
        move_lines = correction_ml or fifo_move._get_out_move_lines()
        moved_qty = 0
        for ml in move_lines:
            fifo_lot = ml.force_fifo_lot_id or ml.lot_id
            if correction_ml:
                moved_qty = quantity
            else:
                moved_qty = ml.product_uom_id._compute_quantity(
                    ml.qty_done, self.uom_id
                )
            fifo_qty = min(remaining_qty, moved_qty)
            self = self.with_context(fifo_lot=fifo_lot, fifo_qty=fifo_qty)
            ml_fifo_vals = super()._run_fifo(fifo_qty, company)
            for key, value in ml_fifo_vals.items():
                if key in ("remaining_qty", "value"):
                    vals[key] += value
                    continue
                vals[key] = value  # unit_cost
            remaining_qty -= fifo_qty
            if float_is_zero(remaining_qty, precision_rounding=self.uom_id.rounding):
                break
        return vals

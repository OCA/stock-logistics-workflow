# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tools import float_is_zero

from odoo.addons.stock_account.models.product import ProductProduct


# flake8: noqa: C901
def post_load_hook():
    def _run_fifo_new(self, quantity, company):
        if not hasattr(self, "_run_fifo_prepare_candidate_update"):
            return self._run_fifo_original(quantity, company)

        self.ensure_one()

        # Find back incoming stock valuation layers (called candidates here)
        # to value `quantity`.
        qty_to_take_on_candidates = quantity
        candidates = (
            self.env["stock.valuation.layer"]
            .sudo()
            .with_context(active_test=False)
            .search(
                [
                    ("product_id", "=", self.id),
                    ("remaining_qty", ">", 0),
                    ("company_id", "=", company.id),
                ]
            )
        )
        new_standard_price = 0
        tmp_value = 0  # to accumulate the value taken on the candidates
        for candidate in candidates:
            qty_taken_on_candidate = min(
                qty_to_take_on_candidates, candidate.remaining_qty
            )

            candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
            new_standard_price = candidate_unit_cost
            value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
            value_taken_on_candidate = candidate.currency_id.round(
                value_taken_on_candidate
            )
            new_remaining_value = candidate.remaining_value - value_taken_on_candidate
            candidate_vals = {
                "remaining_qty": candidate.remaining_qty - qty_taken_on_candidate,
                "remaining_value": new_remaining_value,
            }
            # Start Hook
            candidate_vals = self._run_fifo_prepare_candidate_update(
                candidate,
                qty_taken_on_candidate,
                value_taken_on_candidate,
                candidate_vals,
            )
            # End Hook
            candidate.write(candidate_vals)

            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_value += value_taken_on_candidate
            if float_is_zero(
                qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding
            ):
                break

        # Update the standard price with the price of the last used candidate,
        # if any.
        if new_standard_price and self.cost_method == "fifo":
            self.sudo().with_context(
                force_company=company.id
            ).standard_price = new_standard_price

        # If there's still quantity to value but we're out of candidates,
        # we fall in the
        # negative stock use case. We chose to value the out move at the price
        # of the
        # last out and a correction entry will be made once `_fifo_vacuum`
        # is called.
        vals = {}
        if float_is_zero(
            qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding
        ):
            vals = {
                "value": -tmp_value,
                "unit_cost": tmp_value / quantity,
            }
        else:
            assert qty_to_take_on_candidates > 0
            last_fifo_price = new_standard_price or self.standard_price
            negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
            tmp_value += abs(negative_stock_value)
            vals = {
                "remaining_qty": -qty_to_take_on_candidates,
                "value": -tmp_value,
                "unit_cost": last_fifo_price,
            }
        return vals

    if not hasattr(ProductProduct, "_run_fifo_original"):
        ProductProduct._run_fifo_original = ProductProduct._run_fifo
    ProductProduct._run_fifo = _run_fifo_new

    def _run_fifo_vacuum_new(self, company=None):
        if not hasattr(self, "_run_fifo_prepare_candidate_update"):
            return self._run_fifo_vacuum_original(company=company)
        self.ensure_one()
        if company is None:
            company = self.env.company
        svls_to_vacuum = (
            self.env["stock.valuation.layer"]
            .sudo()
            .search(
                [
                    ("product_id", "=", self.id),
                    ("remaining_qty", "<", 0),
                    ("stock_move_id", "!=", False),
                    ("company_id", "=", company.id),
                ],
                order="create_date, id",
            )
        )
        for svl_to_vacuum in svls_to_vacuum:
            domain = [
                ("company_id", "=", svl_to_vacuum.company_id.id),
                ("product_id", "=", self.id),
                ("remaining_qty", ">", 0),
                "|",
                ("create_date", ">", svl_to_vacuum.create_date),
                "&",
                ("create_date", "=", svl_to_vacuum.create_date),
                ("id", ">", svl_to_vacuum.id),
            ]
            candidates = self.env["stock.valuation.layer"].sudo().search(domain)
            if not candidates:
                break
            qty_to_take_on_candidates = abs(svl_to_vacuum.remaining_qty)
            qty_taken_on_candidates = 0
            tmp_value = 0
            for candidate in candidates:
                qty_taken_on_candidate = min(
                    candidate.remaining_qty, qty_to_take_on_candidates
                )
                qty_taken_on_candidates += qty_taken_on_candidate

                candidate_unit_cost = (
                    candidate.remaining_value / candidate.remaining_qty
                )
                value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
                value_taken_on_candidate = candidate.currency_id.round(
                    value_taken_on_candidate
                )
                new_remaining_value = (
                    candidate.remaining_value - value_taken_on_candidate
                )

                candidate_vals = {
                    "remaining_qty": candidate.remaining_qty - qty_taken_on_candidate,
                    "remaining_value": new_remaining_value,
                }
                # Start Hook
                candidate_vals = self._run_fifo_vacuum_prepare_candidate_update(
                    svl_to_vacuum,
                    candidate,
                    qty_taken_on_candidate,
                    value_taken_on_candidate,
                    candidate_vals,
                )
                # End Hook
                candidate.write(candidate_vals)

                qty_to_take_on_candidates -= qty_taken_on_candidate
                tmp_value += value_taken_on_candidate
                if float_is_zero(
                    qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding
                ):
                    break

            # Get the estimated value we will correct.
            remaining_value_before_vacuum = (
                svl_to_vacuum.unit_cost * qty_taken_on_candidates
            )
            new_remaining_qty = svl_to_vacuum.remaining_qty + qty_taken_on_candidates
            corrected_value = remaining_value_before_vacuum - tmp_value
            svl_to_vacuum.write(
                {"remaining_qty": new_remaining_qty,}
            )

            # Don't create a layer or an accounting entry if the
            # corrected value is zero.
            if svl_to_vacuum.currency_id.is_zero(corrected_value):
                continue

            corrected_value = svl_to_vacuum.currency_id.round(corrected_value)
            move = svl_to_vacuum.stock_move_id
            vals = {
                "product_id": self.id,
                "value": corrected_value,
                "unit_cost": 0,
                "quantity": 0,
                "remaining_qty": 0,
                "stock_move_id": move.id,
                "company_id": move.company_id.id,
                "description": "Revaluation of %s (negative inventory)"
                % move.picking_id.name
                or move.name,
                "stock_valuation_layer_id": svl_to_vacuum.id,
            }
            vacuum_svl = self.env["stock.valuation.layer"].sudo().create(vals)

            # If some negative stock were fixed, we need to recompute
            # the standard price.
            product = self.with_context(force_company=company.id)
            if product.cost_method == "average" and not float_is_zero(
                product.quantity_svl, precision_rounding=self.uom_id.rounding
            ):
                product.sudo().write(
                    {"standard_price": product.value_svl / product.quantity_svl}
                )

            # Create the account move.
            if self.valuation != "real_time":
                continue
            vacuum_svl.stock_move_id._account_entry_move(
                vacuum_svl.quantity,
                vacuum_svl.description,
                vacuum_svl.id,
                vacuum_svl.value,
            )

    if not hasattr(ProductProduct, "_run_fifo_vacuum_original"):
        ProductProduct._run_fifo_vacuum_original = ProductProduct._run_fifo_vacuum
    ProductProduct._run_fifo_vacuum = _run_fifo_vacuum_new

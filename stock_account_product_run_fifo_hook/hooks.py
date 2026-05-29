# Copyright 2026 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.stock_account.models.product import ProductProduct


def post_load_hook():
    def _run_fifo_new(self, quantity, lot=None, at_date=None, location=None):
        self.ensure_one()

        # If no hook is implemented, use original
        if not hasattr(self, "_run_fifo_prepare_candidate_update"):
            return self._run_fifo_original(quantity, lot, at_date, location)

        if self.uom_id.compare(quantity, 0) <= 0:
            if at_date:
                return quantity * self._get_standard_price_at_date(at_date)
            return quantity * self.standard_price
        external_location = location and location.is_valued_external  # noqa: F841

        fifo_cost = 0
        fifo_stack, qty_on_first_move = self._run_fifo_get_stack(
            lot=lot, at_date=at_date, location=location
        )
        last_move = False
        # Going up to get the quantity in the argument
        while quantity > 0 and fifo_stack:
            move = fifo_stack.pop(0)
            last_move = move
            move_value = move.value
            if at_date:
                move_value = move._get_value(at_date=at_date)
            if qty_on_first_move:
                valued_qty = move._get_valued_qty()
                in_qty = qty_on_first_move
                in_value = move_value * in_qty / valued_qty
                qty_on_first_move = 0
            else:
                in_qty = move._get_valued_qty()
                in_value = move_value
            if in_qty > quantity:
                in_value = in_value * quantity / in_qty
                in_qty = quantity
            # Start Hook Prepare Candidate
            valued_move = self.env.context.get("valued_move")
            self._run_fifo_prepare_candidate_update(move, in_qty, in_value, valued_move)
            # End Hook Prepare Candidate
            fifo_cost += in_value
            quantity -= in_qty
        # When we required more quantity than available we extrapolate with
        # the last known price
        if quantity > 0:
            if last_move and last_move.quantity:
                fifo_cost += quantity * (last_move.value / last_move.quantity)
            else:
                fifo_cost += quantity * self.standard_price
        return fifo_cost

    if not hasattr(ProductProduct, "_run_fifo_original"):
        ProductProduct._run_fifo_original = ProductProduct._run_fifo
    ProductProduct._run_fifo = _run_fifo_new

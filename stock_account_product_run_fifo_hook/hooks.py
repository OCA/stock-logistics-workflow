# Copyright 2026 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from collections import defaultdict
from datetime import datetime, timedelta
from typing import NamedTuple

from odoo import models
from odoo.exceptions import UserError

from odoo.addons.stock_account.models.product import ProductProduct
from odoo.addons.stock_account.models.stock_move import StockMove


# START OF HOOK
class FifoCandidate(NamedTuple):
    """Core FifoCandidate with the incoming move the candidate comes from."""

    quantity: float
    value: float
    out_move: models.Model = None
    in_move: models.Model = None


# END OF HOOK


def _get_fifo_value_new(self, quantity, lot=None, stack_size_extra_qty=0):
    """Returns the value for the next outgoing product base on the qty give as
    argument."""
    self.ensure_one()
    # START OF HOOK
    # The patch is global to the process, but the hook method only exists in the
    # databases where this module is installed: use core in the others
    if not hasattr(self, "_run_fifo_prepare_candidate_update"):
        return self._get_fifo_value_original(
            quantity, lot=lot, stack_size_extra_qty=stack_size_extra_qty
        )
    # END OF HOOK
    if self.uom_id.compare(quantity, 0) <= 0:
        std_price = lot.standard_price if lot else self.standard_price
        return quantity * std_price

    fifo_cost = 0
    fifo_stack, qty_on_first_move = self._get_fifo_stack(
        lot=lot, stack_size_extra_qty=stack_size_extra_qty
    )
    last_move = False
    # Going up to get the quantity in the argument
    while quantity > 0 and fifo_stack:
        move = fifo_stack.pop(0)
        last_move = move
        move_value = move.value
        if qty_on_first_move:
            valued_qty = move._get_valued_qty()
            in_qty = qty_on_first_move
            in_value = move_value * in_qty / valued_qty
            qty_on_first_move = 0
        else:
            in_qty = move._get_valued_qty(lot=lot)
            in_value = move_value
            if lot:
                valued_qty = move._get_valued_qty()
                in_value = in_value * in_qty / valued_qty if valued_qty else 0
        if in_qty > quantity:
            in_value = in_value * quantity / in_qty
            in_qty = quantity
        # START OF HOOK
        valued_move = self.env.context.get("valued_move")
        self._run_fifo_prepare_candidate_update(move, in_qty, in_value, valued_move)
        # END OF HOOK
        fifo_cost += in_value
        quantity -= in_qty
    # When we required more quantity than available we extrapolate with the last
    # known price
    if quantity > 0:
        if last_move and last_move.quantity:
            fifo_cost += quantity * (last_move.value / last_move.quantity)
        else:
            fifo_cost += quantity * self.standard_price
    return fifo_cost


def _run_fifo_new(self, at_date=None, lot=None, correction=False):  # noqa: C901
    # START OF HOOK
    # Only the FIFO replay is hooked, and only in the databases where this module
    # is installed
    if not correction or not hasattr(self, "_run_fifo_prepare_candidate_update"):
        return self._run_fifo_original(at_date=at_date, lot=lot, correction=correction)
    # END OF HOOK
    std_price_by_product_id = {}
    value_by_product_id = {}
    stack_by_product = defaultdict(list)
    products = self.sudo()._with_valuation_context()
    if at_date:
        if correction and at_date != datetime.min:  # noqa: DTZ901
            at_date = at_date - timedelta(seconds=1)
        products = products.with_context(to_date=at_date)
        if lot:
            lot = lot.with_context(to_date=at_date)
    qty_by_product = {
        p: (lot.product_qty if lot else p.qty_available) for p in products
    }
    for product in products:
        quantity = qty_by_product.get(product, 0)
        std_price = lot.standard_price if lot else product.standard_price
        if product.uom_id.compare(quantity, 0) < 0:
            if at_date:
                last_in = product._get_last_in(at_date)
                std_price = last_in._get_price_unit() if last_in else std_price
            std_price_by_product_id[product.id] = std_price
            value_by_product_id[product.id] = quantity * std_price
            if correction:
                stack_by_product[product] = [
                    FifoCandidate(quantity, quantity * std_price)
                ]
            continue

        fifo_stack, qty_on_first_move = product._get_fifo_stack(
            lot=lot, at_date=at_date
        )
        value = 0
        for index, move in enumerate(fifo_stack):
            if index == 0 and qty_on_first_move:
                full_qty = move._get_valued_qty()
                valued_qty = qty_on_first_move
                valued_value = (
                    move.value * qty_on_first_move / full_qty if full_qty else 0
                )
            else:
                valued_qty = move._get_valued_qty(lot=lot)
                valued_value = move.value
                if lot:
                    full_qty = move._get_valued_qty()
                    valued_value = move.value * valued_qty / full_qty if full_qty else 0
            value += valued_value
            if correction:
                stack_by_product[product].append(
                    FifoCandidate(valued_qty, valued_value)
                )
                # START OF HOOK
                stack_by_product[product][-1] = stack_by_product[product][-1]._replace(
                    in_move=move
                )
                # END OF HOOK

        std_price = value / quantity if quantity else std_price
        std_price_by_product_id[product.id] = std_price
        value_by_product_id[product.id] = value

    if not correction:
        return std_price_by_product_id, value_by_product_id

    moves_by_product = self._get_stock_moves_with_valuation_by_product(at_date, lot=lot)
    std_price_history_by_product = self._get_std_price_history_by_product(at_date)

    for product in self:
        stack = stack_by_product[product]
        unit_price = std_price_by_product_id.get(product.id, product.standard_price)
        price_changes = iter(
            std_price_history_by_product.get(product, self.env["product.value"])
        )
        next_change = next(price_changes, None)
        for move in moves_by_product.get(product, self.env["stock.move"]):
            while next_change and next_change.date <= move.date:
                unit_price = next_change.value
                # START OF HOOK
                in_moves = [m.in_move for m in stack]
                # END OF HOOK
                stack[:] = [
                    FifoCandidate(m.quantity, m.quantity * unit_price, m.out_move)
                    for m in stack
                ]
                # START OF HOOK
                stack[:] = [
                    m._replace(in_move=in_move)
                    for m, in_move in zip(stack, in_moves, strict=True)
                ]
                # END OF HOOK
                next_change = next(price_changes, None)

            if move.is_in:
                full_in_qty = move._get_valued_qty()
                in_qty = move._get_valued_qty(lot=lot) if lot else full_in_qty
                unit_price = move.value / full_in_qty if full_in_qty else unit_price
                while in_qty > 0 and stack and stack[0].quantity < 0:
                    shortage_move = stack[0]
                    shortage = -shortage_move.quantity
                    filled = min(shortage, in_qty)
                    if shortage_move.out_move:
                        old_unit = shortage_move.value / shortage_move.quantity
                        shortage_move.out_move.value += filled * (old_unit - unit_price)
                        # START OF HOOK
                        product._run_fifo_prepare_candidate_update(
                            move, filled, filled * unit_price, shortage_move.out_move
                        )
                        # END OF HOOK
                    in_qty -= filled
                    remaining_qty = shortage_move.quantity + filled
                    if remaining_qty < 0:
                        stack[0] = FifoCandidate(
                            remaining_qty,
                            remaining_qty * unit_price,
                            shortage_move.out_move,
                        )
                    else:
                        stack.pop(0)
                if in_qty > 0:
                    stack.append(FifoCandidate(in_qty, in_qty * unit_price))
                    # START OF HOOK
                    stack[-1] = stack[-1]._replace(in_move=move)
                    # END OF HOOK
            elif move.is_out:
                out_qty = (
                    move._get_valued_qty(lot=lot) if lot else move._get_valued_qty()
                )
                out_value = 0
                while out_qty > 0 and stack and stack[0].quantity > 0:
                    candidate_qty, candidate_value = stack[0].quantity, stack[0].value
                    # START OF HOOK
                    candidate_move = stack[0].in_move
                    # END OF HOOK
                    if candidate_qty > out_qty:
                        consumed_value = candidate_value * out_qty / candidate_qty
                        stack[0] = FifoCandidate(
                            candidate_qty - out_qty, candidate_value - consumed_value
                        )
                        # START OF HOOK
                        stack[0] = stack[0]._replace(in_move=candidate_move)
                        if candidate_move:
                            product._run_fifo_prepare_candidate_update(
                                candidate_move, out_qty, consumed_value, move
                            )
                        # END OF HOOK
                        out_value += consumed_value
                        out_qty = 0
                    else:
                        # START OF HOOK
                        if candidate_move:
                            product._run_fifo_prepare_candidate_update(
                                candidate_move, candidate_qty, candidate_value, move
                            )
                        # END OF HOOK
                        out_value += candidate_value
                        out_qty -= candidate_qty
                        stack.pop(0)
                if out_qty > 0:
                    out_value += out_qty * unit_price
                    stack.append(FifoCandidate(-out_qty, -out_qty * unit_price, move))
                if lot:
                    move.value -= out_value
                elif move.value != -out_value:
                    move.value = -out_value

        std_price_by_product_id[product.id] = unit_price
        value_by_product_id[product.id] = sum(
            stack_tuple.value for stack_tuple in stack
        )

    return std_price_by_product_id, value_by_product_id


def _set_value_new(self, recompute_date=None, skip_check=False):  # noqa: C901
    """Set the value of the move.

    :param recompute_date: if provided, valuation runs in correction mode. The given
        moves changed position in the valuation timeline (their date moved, or the
        quantity of one of their lines was edited), which shifts the on-hand context
        of every later move. The valuation of every impacted product is therefore
        replayed from ``recompute_date`` (the earliest impacted date among the moves)
        through
    :param skip_check: internal flag set while replaying, to only refresh in-move
        values without re-triggering the replay detection below (which would loop).
    :return: the outgoing moves whose value changed during a valuation replay.
    """
    # START OF HOOK
    # The patch is global to the process, but the hook method only exists in the
    # databases where this module is installed: use core in the others
    if not hasattr(self.env["product.product"], "_run_fifo_prepare_candidate_update"):
        return self._set_value_original(
            recompute_date=recompute_date, skip_check=skip_check
        )
    # END OF HOOK
    changed_moves = self.env["stock.move"]
    moves_already_sold = self.filtered(
        lambda m: m.is_in and m.remaining_qty != m._get_valued_qty()
    )
    if not recompute_date and not skip_check and moves_already_sold:
        recompute_date = min(self.mapped("date"))
        for move in moves_already_sold:
            product = move.product_id.with_company(move.company_id)
            if product.cost_method != "fifo":
                continue
            oversold_stack = product._get_fifo_stack(
                at_date=move.date - timedelta(seconds=1), allow_negative=True
            )[0]
            oversold_moves = (
                self.env["stock.move"]
                .concat(oversold_stack)
                .filtered(lambda m: m.is_out)
            )
            if oversold_moves:
                recompute_date = min(recompute_date, *oversold_moves.mapped("date"))
        self._set_value(recompute_date=recompute_date)
        return changed_moves

    if recompute_date and any(
        m.remaining_qty != m._get_valued_qty() or m.is_out for m in self
    ):
        self.filtered(lambda m: m.is_in)._set_value(skip_check=True)
        return self.product_id._correct_inventory_valuation(recompute_date)

    self = self.sorted(key=lambda m: (m.date, m.id))
    products_to_recompute = set()
    lots_to_recompute = set()
    fifo_qty_already_processed = defaultdict(float)
    for move in self:
        move = move.with_company(move.company_id)
        if not move.is_out or move.product_id.cost_method != "fifo":
            continue
        if move.product_id.lot_valuated:
            for move_line in move.move_line_ids.filtered("lot_id"):
                fifo_qty_already_processed[move_line.lot_id] -= (
                    move_line.quantity_product_uom
                )
        else:
            fifo_qty_already_processed[move.product_id] -= move._get_valued_qty()

    for move in self:
        move = move.with_company(move.company_id)
        if move.is_in:
            products_to_recompute.add(move.product_id.id)
            if move.product_id.lot_valuated:
                if any(not ml.lot_id for ml in move.move_line_ids):
                    raise UserError(
                        self.env._(
                            "A lot/serial number is required for product '%s' as "
                            "it has lot valuation enabled.",
                            move.product_id.display_name,
                        )
                    )
                lots_to_recompute.update(move.move_line_ids.lot_id.ids)
            move.value = move.sudo()._get_value()
            continue
        # Outgoing moves
        if not move.is_out:
            continue
        if move.product_id.cost_method == "fifo" or (
            move.product_id.cost_method == "average" and move.product_id.lot_valuated
        ):
            products_to_recompute.add(move.product_id.id)
        if move.product_id.lot_valuated and move.product_id.cost_method != "standard":
            lots_to_recompute.update(move.move_line_ids.lot_id.ids)
        if move.product_id.cost_method == "fifo":
            # START OF HOOK
            move = move.with_context(valued_move=move)
            # END OF HOOK
            if not move.product_id.lot_valuated:
                valued_qty = move._get_valued_qty()
                move.value = -move.product_id._get_fifo_value(
                    valued_qty,
                    stack_size_extra_qty=-fifo_qty_already_processed[move.product_id],
                )
                fifo_qty_already_processed[move.product_id] += valued_qty
            else:
                value = 0.0
                for move_line in move.move_line_ids:
                    ml_qty = move_line.quantity_product_uom
                    if move_line.lot_id:
                        value += move.product_id._get_fifo_value(
                            ml_qty,
                            lot=move_line.lot_id,
                            stack_size_extra_qty=-fifo_qty_already_processed[
                                move_line.lot_id
                            ],
                        )
                        fifo_qty_already_processed[move_line.lot_id] += ml_qty
                    else:
                        value += move.product_id.standard_price * ml_qty
                move.value = -value
        else:
            if not move.product_id.lot_valuated:
                move.value = -move.product_id.standard_price * move._get_valued_qty()
            else:
                value = 0.0
                for move_line in move.move_line_ids:
                    price = (
                        move_line.lot_id.standard_price
                        if move_line.lot_id
                        else move.product_id.standard_price
                    )
                    value += price * move_line.quantity_product_uom
                move.value = -value

    # Recompute the standard price
    self.env["product.product"].browse(products_to_recompute)._update_standard_price()
    self.env["stock.lot"].browse(lots_to_recompute)._update_standard_price()
    return changed_moves


def post_load_hook():
    if not hasattr(ProductProduct, "_get_fifo_value_original"):
        ProductProduct._get_fifo_value_original = ProductProduct._get_fifo_value
    ProductProduct._get_fifo_value = _get_fifo_value_new
    if not hasattr(StockMove, "_set_value_original"):
        StockMove._set_value_original = StockMove._set_value
    StockMove._set_value = _set_value_new
    if not hasattr(ProductProduct, "_run_fifo_original"):
        ProductProduct._run_fifo_original = ProductProduct._run_fifo
    ProductProduct._run_fifo = _run_fifo_new

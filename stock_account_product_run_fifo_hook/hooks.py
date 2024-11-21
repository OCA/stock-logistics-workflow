# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from collections import defaultdict
from datetime import datetime

from odoo import _
from odoo.exceptions import UserError
from odoo.tools import clean_context, float_compare, float_is_zero, float_round

from odoo.addons.stock_account.models.product import ProductProduct
from odoo.addons.stock_account.models.stock_move import StockMove


# flake8: noqa: C901
def post_load_hook():
    def _run_fifo_new(self, quantity, company):
        if not hasattr(self, "_run_fifo_prepare_candidate_update"):
            return self._run_fifo_original(quantity, company)

        # Find back incoming stock valuation layers (called candidates here)
        # to value `quantity`.
        qty_to_take_on_candidates = quantity
        candidates = self._get_fifo_candidates(company)
        new_standard_price = 0
        tmp_value = 0  # to accumulate the value taken on the candidates
        taken_data = {}
        for candidate in candidates:
            qty_taken_on_candidate = min(
                qty_to_take_on_candidates, candidate.remaining_qty
            )
            taken_data[candidate.id] = {"quantity": qty_taken_on_candidate}
            candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
            new_standard_price = candidate_unit_cost
            # HOOK value taken on candidate
            value_taken_on_candidate = candidate._fifo_new_get_value_taken_on_candidate(
                qty_taken_on_candidate, candidate_unit_cost
            )
            # END HOOK value taken on candidate
            taken_data[candidate.id].update(
                {
                    "value": value_taken_on_candidate,
                }
            )
            new_remaining_value = candidate.remaining_value - value_taken_on_candidate
            candidate_vals = {
                "remaining_qty": candidate.remaining_qty - qty_taken_on_candidate,
                "remaining_value": new_remaining_value,
            }
            # Start Hook Prepare Candidate
            candidate_vals = self._run_fifo_prepare_candidate_update(
                candidate,
                qty_taken_on_candidate,
                value_taken_on_candidate,
                candidate_vals,
            )
            # End Hook Prepare Candidate
            candidate.write(candidate_vals)

            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_value += value_taken_on_candidate
            if float_is_zero(
                qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding
            ):
                if float_is_zero(
                    candidate.remaining_qty, precision_rounding=self.uom_id.rounding
                ):
                    next_candidates = candidates.filtered(
                        lambda svl: svl.remaining_qty > 0
                    )
                    new_standard_price = (
                        next_candidates
                        and next_candidates[0].unit_cost
                        or new_standard_price
                    )
                break

        # Update the standard price with the price of the last used candidate,
        # if any.
        # START HOOK update standard price
        if hasattr(self, "_price_updateable"):
            if self._price_updateable(new_standard_price):
                self.sudo().with_company(company.id).with_context(
                    disable_auto_svl=True
                ).standard_price = new_standard_price
        else:
            if new_standard_price and self.cost_method == "fifo":
                self.sudo().with_company(company.id).with_context(
                    disable_auto_svl=True
                ).standard_price = new_standard_price
        # END HOOK update standard price
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
                "taken_data": taken_data,
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
        if company is None:
            company = self.env.company
        ValuationLayer = self.env["stock.valuation.layer"].sudo()
        svls_to_vacuum_by_product = defaultdict(lambda: ValuationLayer)
        res = ValuationLayer.read_group(
            [
                ("product_id", "in", self.ids),
                ("remaining_qty", "<", 0),
                ("stock_move_id", "!=", False),
                ("company_id", "=", company.id),
            ],
            ["ids:array_agg(id)", "create_date:min"],
            ["product_id"],
            orderby="create_date, id",
        )
        min_create_date = datetime.max
        for group in res:
            svls_to_vacuum_by_product[group["product_id"][0]] = ValuationLayer.browse(
                group["ids"]
            )
            min_create_date = min(min_create_date, group["create_date"])
        all_candidates_by_product = defaultdict(lambda: ValuationLayer)
        domain = [
            ("product_id", "in", self.ids),
            ("remaining_qty", ">", 0),
            ("company_id", "=", company.id),
            ("create_date", ">=", min_create_date),
        ]
        if self.env.context.get("use_past_svl", False):
            domain = domain[:3]
        res = ValuationLayer.sudo().read_group(
            domain,
            ["ids:array_agg(id)"],
            ["product_id"],
            orderby="id",
        )
        for group in res:
            all_candidates_by_product[group["product_id"][0]] = ValuationLayer.browse(
                group["ids"]
            )

        new_svl_vals_real_time = []
        new_svl_vals_manual = []
        real_time_svls_to_vacuum = ValuationLayer

        for product in self:
            all_candidates = all_candidates_by_product[product.id]
            current_real_time_svls = ValuationLayer
            for svl_to_vacuum in svls_to_vacuum_by_product[product.id]:
                # We don't use search to avoid executing _flush_search and to decrease interaction with DB
                candidates = all_candidates.filtered(
                    lambda r: r.create_date > svl_to_vacuum.create_date
                    or r.create_date == svl_to_vacuum.create_date
                    and r.id > svl_to_vacuum.id
                )
                if self.env.context.get("use_past_svl", False):
                    candidates = all_candidates
                if not candidates:
                    break
                qty_to_take_on_candidates = abs(svl_to_vacuum.remaining_qty)
                qty_taken_on_candidates = 0
                tmp_value = 0
                taken_data = {}
                for candidate in candidates:
                    qty_taken_on_candidate = min(
                        candidate.remaining_qty, qty_to_take_on_candidates
                    )
                    qty_taken_on_candidates += qty_taken_on_candidate

                    taken_data[candidate.id] = {"quantity": qty_taken_on_candidate}

                    candidate_unit_cost = (
                        candidate.remaining_value / candidate.remaining_qty
                    )
                    # HOOK value taken on candidate
                    value_taken_on_candidate = (
                        candidate._fifo_vacuum_get_value_taken_on_candidate(
                            qty_taken_on_candidate, candidate_unit_cost
                        )
                    )
                    # END HOOK value taken on candidate

                    taken_data[candidate.id].update(
                        {
                            "value": value_taken_on_candidate,
                        }
                    )

                    new_remaining_value = (
                        candidate.remaining_value - value_taken_on_candidate
                    )

                    candidate_vals = {
                        "remaining_qty": candidate.remaining_qty
                        - qty_taken_on_candidate,
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
                    if not (candidate.remaining_qty > 0):
                        all_candidates -= candidate

                    qty_to_take_on_candidates -= qty_taken_on_candidate
                    tmp_value += value_taken_on_candidate
                    if float_is_zero(
                        qty_to_take_on_candidates,
                        precision_rounding=product.uom_id.rounding,
                    ):
                        break

                # Get the estimated value we will correct.
                remaining_value_before_vacuum = (
                    svl_to_vacuum.unit_cost * qty_taken_on_candidates
                )
                new_remaining_qty = (
                    svl_to_vacuum.remaining_qty + qty_taken_on_candidates
                )
                corrected_value = remaining_value_before_vacuum - tmp_value
                svl_to_vacuum.with_context(taken_data=taken_data).write(
                    {
                        "remaining_qty": new_remaining_qty,
                    }
                )

                # Don't create a layer or an accounting entry if the corrected value is zero.
                if svl_to_vacuum.currency_id.is_zero(corrected_value):
                    continue

                # HOOK: round corrected value
                corrected_value = svl_to_vacuum._fifo_vacuum_get_corrected_value(
                    corrected_value
                )
                # END HOOK: round corrected value

                move = svl_to_vacuum.stock_move_id
                new_svl_vals = (
                    new_svl_vals_real_time
                    if product.valuation == "real_time"
                    else new_svl_vals_manual
                )
                new_svl_vals.append(
                    {
                        "product_id": product.id,
                        "value": corrected_value,
                        "unit_cost": 0,
                        "quantity": 0,
                        "remaining_qty": 0,
                        "stock_move_id": move.id,
                        "company_id": move.company_id.id,
                        "description": "Revaluation of %s (negative inventory)"
                        % (move.picking_id.name or move.name),
                        "stock_valuation_layer_id": svl_to_vacuum.id,
                    }
                )
                if product.valuation == "real_time":
                    current_real_time_svls |= svl_to_vacuum
            real_time_svls_to_vacuum |= current_real_time_svls
        ValuationLayer.create(new_svl_vals_manual)
        vacuum_svls = ValuationLayer.create(new_svl_vals_real_time)

        # If some negative stock were fixed, we need to recompute the standard price.
        for product in self:
            product = product.with_company(company.id)
            # Only recompute if we fixed some negative stock
            if not svls_to_vacuum_by_product[product.id]:
                continue
            if product.cost_method == "average" and not float_is_zero(
                product.quantity_svl, precision_rounding=product.uom_id.rounding
            ):
                product.sudo().with_context(disable_auto_svl=True).write(
                    {"standard_price": product.value_svl / product.quantity_svl}
                )

        vacuum_svls._validate_accounting_entries()
        self._create_fifo_vacuum_anglo_saxon_expense_entries(
            zip(vacuum_svls, real_time_svls_to_vacuum)
        )

    if not hasattr(ProductProduct, "_run_fifo_vacuum_original"):
        ProductProduct._run_fifo_vacuum_original = ProductProduct._run_fifo_vacuum
    ProductProduct._run_fifo_vacuum = _run_fifo_vacuum_new

    def _prepare_out_svl_vals_new(self, quantity, company):
        """Prepare the values for a stock valuation layer created by a delivery.

        :param quantity: the quantity to value, expressed in `self.uom_id`
        :return: values to use in a call to create
        :rtype: dict
        """
        self.ensure_one()
        company_id = self.env.context.get("force_company", self.env.company.id)
        company = self.env["res.company"].browse(company_id)
        currency = company.currency_id
        # Quantity is negative for out valuation layers.
        quantity = -1 * quantity
        vals = {
            "product_id": self.id,
            "value": self._get_rounded_value(quantity, currency),  # HOOK: rounded value
            "unit_cost": self.standard_price,
            "quantity": quantity,
        }
        fifo_vals = self._run_fifo(abs(quantity), company)
        vals["remaining_qty"] = fifo_vals.get("remaining_qty")
        # In case of AVCO, fix rounding issue of standard price when needed.
        if self.product_tmpl_id.cost_method == "average" and not float_is_zero(
            self.quantity_svl, precision_rounding=self.uom_id.rounding
        ):
            # HOOK: rounding error
            rounding_error = self._get_rounded_error(currency, quantity)
            # END HOOK: rounding error
            if rounding_error:
                # If it is bigger than the (smallest number of the currency * quantity) / 2,
                # then it isn't a rounding error but a stock valuation error, we shouldn't fix it under the hood ...
                if abs(rounding_error) <= max(
                    (abs(quantity) * currency.rounding) / 2, currency.rounding
                ):
                    vals["value"] += rounding_error
                    vals["rounding_adjustment"] = "\nRounding Adjustment: %s%s %s" % (
                        "+" if rounding_error > 0 else "",
                        float_repr(
                            rounding_error, precision_digits=currency.decimal_places
                        ),
                        currency.symbol,
                    )
        if self.product_tmpl_id.cost_method == "fifo":
            vals.update(fifo_vals)
        return vals

    def _change_standard_price_new(self, new_price):
        """Helper to create the stock valuation layers and the account moves
        after an update of standard price.

        :param new_price: new standard price
        """
        # Handle stock valuation layers.

        if self.filtered(lambda p: p.valuation == "real_time") and not self.env[
            "stock.valuation.layer"
        ].check_access_rights("read", raise_exception=False):
            raise UserError(
                _(
                    "You cannot update the cost of a product in automated valuation as it leads to the creation of a journal entry, for which you don't have the access rights."
                )
            )

        svl_vals_list = []
        company_id = self.env.company
        price_unit_prec = self.env["decimal.precision"].precision_get("Product Price")
        rounded_new_price = float_round(new_price, precision_digits=price_unit_prec)
        for product in self:
            if product.cost_method not in ("standard", "average"):
                continue
            quantity_svl = product.sudo().quantity_svl
            if (
                float_compare(
                    quantity_svl, 0.0, precision_rounding=product.uom_id.rounding
                )
                <= 0
            ):
                continue
            value_svl = product.sudo().value_svl
            # HOOK: value diff
            value = product._get_change_price_diff_value(
                company_id, rounded_new_price, quantity_svl, value_svl
            )
            # END HOOK: value diff
            if company_id.currency_id.is_zero(value):
                continue

            # pylint: disable=W8120
            svl_vals = {
                "company_id": company_id.id,
                "product_id": product.id,
                "description": _("Product value manually modified (from %s to %s)")
                % (product.standard_price, rounded_new_price),
                "value": value,
                "quantity": 0,
            }
            svl_vals_list.append(svl_vals)
        stock_valuation_layers = (
            self.env["stock.valuation.layer"].sudo().create(svl_vals_list)
        )

        # Handle account moves.
        product_accounts = {
            product.id: product.product_tmpl_id.get_product_accounts()
            for product in self
        }
        am_vals_list = []
        for stock_valuation_layer in stock_valuation_layers:
            product = stock_valuation_layer.product_id
            value = stock_valuation_layer.value

            if product.type != "product" or product.valuation != "real_time":
                continue

            # Sanity check.
            if not product_accounts[product.id].get("expense"):
                raise UserError(
                    _("You must set a counterpart account on your product category.")
                )
            if not product_accounts[product.id].get("stock_valuation"):
                raise UserError(
                    _(
                        "You don't have any stock valuation account defined on your product category. You must define one before processing this operation."
                    )
                )

            if value < 0:
                debit_account_id = product_accounts[product.id]["expense"].id
                credit_account_id = product_accounts[product.id]["stock_valuation"].id
            else:
                debit_account_id = product_accounts[product.id]["stock_valuation"].id
                credit_account_id = product_accounts[product.id]["expense"].id

            move_vals = {
                "journal_id": product_accounts[product.id]["stock_journal"].id,
                "company_id": company_id.id,
                "ref": product.default_code,
                "stock_valuation_layer_ids": [(6, None, [stock_valuation_layer.id])],
                "move_type": "entry",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": _(
                                "%(user)s changed cost from %(previous)s to %(new_price)s - %(product)s",
                                user=self.env.user.name,
                                previous=product.standard_price,
                                new_price=new_price,
                                product=product.display_name,
                            ),
                            "account_id": debit_account_id,
                            "debit": abs(value),
                            "credit": 0,
                            "product_id": product.id,
                            "quantity": 0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": _(
                                "%(user)s changed cost from %(previous)s to %(new_price)s - %(product)s",
                                user=self.env.user.name,
                                previous=product.standard_price,
                                new_price=new_price,
                                product=product.display_name,
                            ),
                            "account_id": credit_account_id,
                            "debit": 0,
                            "credit": abs(value),
                            "product_id": product.id,
                            "quantity": 0,
                        },
                    ),
                ],
            }
            am_vals_list.append(move_vals)

        # pylint: disable=W8121
        account_moves = (
            self.env["account.move"]
            .sudo()
            .with_context(clean_context(self._context))
            .create(am_vals_list)
        )
        if account_moves:
            account_moves._post()

    if not hasattr(ProductProduct, "_prepare_out_svl_vals_original"):
        ProductProduct._prepare_out_svl_vals_original = (
            ProductProduct._prepare_out_svl_vals
        )
    ProductProduct._prepare_out_svl_vals = _prepare_out_svl_vals_new

    if not hasattr(ProductProduct, "_change_standard_price_original"):
        ProductProduct._change_standard_price_original = (
            ProductProduct._change_standard_price
        )
    ProductProduct._change_standard_price = _change_standard_price_new

    def _create_out_svl_new(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_out_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(
                    valued_move_line.qty_done, move.product_id.uom_id
                )
            if float_is_zero(
                forced_quantity or valued_quantity,
                precision_rounding=move.product_id.uom_id.rounding,
            ):
                continue
            svl_vals = move.product_id.with_context(
                move_requestor=move.id
            )._prepare_out_svl_vals(forced_quantity or valued_quantity, move.company_id)
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals["description"] = (
                    _("Correction of %s (modification of past move)")
                    % move.picking_id.name
                    or move.name
                )
            svl_vals["description"] += svl_vals.pop("rounding_adjustment", "")
            svl_vals_list.append(svl_vals)
        return self.env["stock.valuation.layer"].sudo().create(svl_vals_list)

    if not hasattr(StockMove, "_create_out_svl_original"):
        StockMove._create_out_svl_original = StockMove._create_out_svl
    StockMove._create_out_svl = _create_out_svl_new

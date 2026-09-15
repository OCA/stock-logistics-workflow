# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
from collections import defaultdict

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

WATERMARK_PARAM = "stock_valuation_fifo_lot_allocation.backfill_last_id"
BALANCED_PARAM = "stock_valuation_fifo_lot_allocation.backfill_balanced"


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    lot_allocation_ids = fields.One2many(
        "stock.valuation.lot.allocation",
        "valuation_layer_id",
        string="Lot Allocations",
    )

    @api.model_create_multi
    def create(self, vals_list):
        layers = super().create(vals_list)
        # Only value-only layers (landed costs, price differences, revaluations) are
        # handled here. Quantity-bearing layers are handled from stock.move, where
        # the per-lot figures become available only after the incoming quantities
        # have been written / the FIFO run has walked the move lines.
        layers.filtered(lambda x: not x.quantity)._create_lot_allocations()
        return layers

    def _is_lot_allocation_applicable(self):
        self.ensure_one()
        product = self.product_id.with_company(self.company_id)
        return (
            product.cost_method == "fifo"
            and product.tracking != "none"
            and not self.currency_id.is_zero(self.value)
        )

    def _get_value_only_scope_lines(self):
        """Return the move lines a value-only layer adds its value to.

        Landed costs and price differences are scoped to the move they correct
        (directly or through the layer they correct); a product-wide revaluation
        spreads over everything the product still holds in stock.
        """
        self.ensure_one()
        move = self.stock_move_id or self.stock_valuation_layer_id.stock_move_id
        if move:
            return move.move_line_ids.filtered(
                lambda x: x.lot_id and x.qty_remaining > 0
            )
        return self.env["stock.move.line"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("company_id", "=", self.company_id.id),
                ("qty_remaining", ">", 0),
            ]
        )

    def _get_lot_allocation_basis(self):
        """Return {lot: quantity} to prorate the layer value on."""
        self.ensure_one()
        basis = defaultdict(float)
        product_uom = self.product_id.uom_id
        if self.quantity > 0:
            # Incoming: unit_cost is uniform over the layer, so quantity is exact.
            for ml in self.stock_move_id.move_line_ids.filtered("lot_id"):
                basis[ml.lot_id] += ml.qty_base
        elif self.quantity < 0:
            # Outgoing layers are allocated from the FIFO run at the time the layer
            # is created (see stock.move._create_out_svl); this branch is only
            # reached by the backfill, where that detail is gone. Prorating by
            # quantity is approximate when the move spans lots of differing costs;
            # the residual is picked up by the balancing pass.
            for ml in self.stock_move_id.move_line_ids.filtered("lot_id"):
                lot = ml.force_fifo_lot_id or ml.lot_id
                basis[lot] += ml.product_uom_id._compute_quantity(
                    ml.qty_done, product_uom
                )
        else:
            for ml in self._get_value_only_scope_lines():
                basis[ml.lot_id] += ml.qty_remaining
        return {lot: qty for lot, qty in basis.items() if qty}

    def _get_lot_allocation_amounts(self):
        """Return the unrounded {lot: amount} split of the layer value."""
        self.ensure_one()
        basis = self._get_lot_allocation_basis()
        total = sum(basis.values())
        if not total:
            # Nothing in stock to carry the value.
            return {}
        return {lot: self.value * qty / total for lot, qty in basis.items()}

    def _round_lot_allocation(self, amounts_by_lot):
        """Round the per-lot amounts and give the remainder to the largest one, so
        that the allocation adds up to the layer value to the cent."""
        self.ensure_one()
        currency = self.currency_id
        amounts = {
            lot: currency.round(amount) for lot, amount in amounts_by_lot.items()
        }
        remainder = currency.round(self.value - sum(amounts.values()))
        if amounts and not currency.is_zero(remainder):
            largest = sorted(amounts, key=lambda lot: (-abs(amounts[lot]), lot.id))[0]
            amounts[largest] += remainder
        return amounts

    def _prepare_lot_allocation_vals(self, amounts_by_lot, description=None):
        self.ensure_one()
        return [
            {
                "lot_id": lot.id,
                "valuation_layer_id": self.id,
                "allocated_amount": amount,
                "description": description or self.description,
            }
            for lot, amount in amounts_by_lot.items()
            if not self.currency_id.is_zero(amount)
        ]

    def _create_lot_allocations(self, amounts_by_lot=None):
        """Record how much of each layer's value is charged to each lot/serial.

        ``amounts_by_lot`` is only passed for outgoing layers, whose exact per-lot
        values are taken from the FIFO run instead of being prorated.
        """
        vals_list = []
        for layer in self:
            # Idempotent: a layer that already has allocations is never touched
            # again, so the backfill can be re-run or overlap with a manual run.
            if not layer._is_lot_allocation_applicable() or layer.lot_allocation_ids:
                continue
            amounts = (
                layer._get_lot_allocation_amounts()
                if amounts_by_lot is None
                else amounts_by_lot
            )
            vals_list += layer._prepare_lot_allocation_vals(
                layer._round_lot_allocation(amounts)
            )
        return self.env["stock.valuation.lot.allocation"].sudo().create(vals_list)

    @api.model
    def _get_backfill_watermark(self):
        return int(self.env["ir.config_parameter"].sudo().get_param(WATERMARK_PARAM, 0))

    @api.model
    def _set_backfill_watermark(self, last_id):
        self.env["ir.config_parameter"].sudo().set_param(WATERMARK_PARAM, last_id)

    @api.model
    def _balance_lot_allocations(self):
        """Close the gap the backfill cannot compute exactly.

        Historical outgoing and value-only layers are allocated on the current
        remaining quantities rather than the as-of-date ones, so the ledger can
        drift from the lots' remaining value. One adjustment row per lot restores
        the invariant and keeps every approximation visible in a single auditable
        record instead of smearing it across history.
        """
        params = self.env["ir.config_parameter"].sudo()
        if params.get_param(BALANCED_PARAM):
            return
        gaps = defaultdict(float)
        groups = (
            self.env["stock.move.line"]
            .sudo()
            .read_group(
                [("qty_remaining", ">", 0)], ["value_remaining:sum"], ["lot_id"]
            )
        )
        for group in groups:
            if group["lot_id"]:
                gaps[group["lot_id"][0]] += group["value_remaining"]
        allocations = self.env["stock.valuation.lot.allocation"].sudo()
        for group in allocations.read_group([], ["allocated_amount:sum"], ["lot_id"]):
            gaps[group["lot_id"][0]] -= group["allocated_amount"]
        vals_list = []
        for lot_id, gap in gaps.items():
            layer = self.sudo().search(
                [("lot_ids", "in", lot_id), ("quantity", ">", 0)],
                order="id desc",
                limit=1,
            )
            if not layer:
                _logger.warning(
                    "No incoming valuation layer found for lot %s; its allocation "
                    "gap of %s is left unbalanced.",
                    lot_id,
                    gap,
                )
                continue
            if layer.currency_id.is_zero(gap):
                continue
            vals_list += layer._prepare_lot_allocation_vals(
                {self.env["stock.lot"].browse(lot_id): gap},
                description=_("Opening allocation adjustment"),
            )
        allocations.create(vals_list)
        params.set_param(BALANCED_PARAM, "1")

    @api.model
    def _cron_backfill_lot_allocations(self, batch=2000, max_batches=20):
        """Allocate the pre-existing valuation layers, oldest first.

        Progress is a watermark rather than a flag on the layer: it cannot drift
        out of sync with the allocation rows, and a rebuild is just "delete the
        allocations and reset the parameter".
        """
        layers = self.sudo()
        for _batch in range(max_batches):
            svls = layers.search(
                [("id", ">", self._get_backfill_watermark())], order="id", limit=batch
            )
            if not svls:
                self._balance_lot_allocations()
                cron = self.env.ref(
                    "stock_valuation_fifo_lot_allocation."
                    "ir_cron_lot_allocation_backfill",
                    raise_if_not_found=False,
                )
                if cron:
                    cron.active = False
                break
            svls._create_lot_allocations()
            self._set_backfill_watermark(svls[-1].id)
            # Commit per batch: short locks, and a crash resumes where it stopped.
            self.env.cr.commit()  # pylint: disable=invalid-commit

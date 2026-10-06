# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from collections import defaultdict

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_fifo_candidate_lines(self):
        """Return the move lines whose FIFO balance an outgoing move can consume."""
        self.ensure_one()
        return self.env["stock.move.line"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("company_id", "=", self.company_id.id),
                ("qty_remaining", ">", 0),
            ]
        )

    def _create_out_lot_allocations(self, layer, consumed_before):
        """Allocate an outgoing layer from what the FIFO run actually consumed.

        The layer is an aggregate: a single value and unit cost for a move that may
        span lots bought at different costs, so no arithmetic on it recovers the
        per-lot split. The dependency writes that split down as it walks the move
        lines, incrementing ``value_consumed`` on the incoming line of the lot whose
        FIFO balance is being consumed, so the per-lot values of this move are the
        increase of ``value_consumed`` it caused.
        """
        self.ensure_one()
        if not layer or not layer._is_lot_allocation_applicable():
            return
        amounts = defaultdict(float)
        for ml, before in consumed_before.items():
            consumed = ml.value_consumed - before
            if consumed:
                # value_consumed grows as the value leaves the lot, hence the sign.
                amounts[ml.lot_id] -= consumed
        layer._create_lot_allocations(amounts_by_lot=amounts)

    def _create_in_svl(self, forced_quantity=None):
        layers = super()._create_in_svl(forced_quantity=forced_quantity)
        # qty_base, the allocation basis, is written by stock_valuation_fifo_lot
        # within the super call, so the split can only be computed once it returns.
        layers._create_lot_allocations()
        return layers

    def _create_out_svl(self, forced_quantity=None):
        layers = self.env["stock.valuation.layer"]
        for move in self:
            candidates = move._get_fifo_candidate_lines()
            consumed_before = {ml: ml.value_consumed for ml in candidates}
            layer = super(StockMove, move)._create_out_svl(
                forced_quantity=forced_quantity
            )
            layers |= layer
            move._create_out_lot_allocations(layer, consumed_before)
        return layers

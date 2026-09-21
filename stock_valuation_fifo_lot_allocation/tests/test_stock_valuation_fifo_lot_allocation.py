# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged

from odoo.addons.stock_valuation_fifo_lot.tests.common import (
    TestStockValuationFifoCommon,
)


@tagged("post_install", "-at_install")
class TestStockValuationLotAllocation(TestStockValuationFifoCommon):
    def _get_lot(self, name):
        return self.env["stock.lot"].search(
            [("product_id", "=", self.product.id), ("name", "=", name)], limit=1
        )

    def _get_allocations(self, layer=None, lot=None):
        domain = [("product_id", "=", self.product.id)]
        if layer:
            domain.append(("valuation_layer_id", "=", layer.id))
        if lot:
            domain.append(("lot_id", "=", lot.id))
        return self.env["stock.valuation.lot.allocation"].search(domain)

    def _get_amounts_by_lot_name(self, layer):
        return {
            allocation.lot_id.name: allocation.allocated_amount
            for allocation in self._get_allocations(layer=layer)
        }

    def _get_expense_account(self):
        return self.env["account.account"].search(
            [("account_type", "=", "expense")], limit=1
        )

    def _create_value_only_layer(self, value, move=None, layer=None):
        """Create a layer with the vals landed costs and price differences use,
        i.e. value only, with the scope expressed either by the move or by the
        layer it corrects, and the value added to that layer's remaining value."""
        new_layer = self.env["stock.valuation.layer"].create(
            {
                "product_id": self.product.id,
                "company_id": self.env.company.id,
                "description": "Test value-only layer",
                "value": value,
                "unit_cost": 0,
                "quantity": 0,
                "remaining_qty": 0,
                "stock_move_id": move.id if move else False,
                "stock_valuation_layer_id": layer.id if layer else False,
            }
        )
        layer.remaining_value += value
        return new_layer

    def _assert_invariant(self):
        """The acceptance criterion of the ledger: what it says a lot is worth has
        to be what the FIFO valuation says the lot is worth. Per lot this holds to
        the cent, as the rounding remainder of a layer is given to a single lot;
        over the product it holds exactly."""
        move_lines = self.env["stock.move.line"].search(
            [("product_id", "=", self.product.id)]
        )
        for lot in move_lines.mapped("lot_id"):
            remaining = sum(
                move_lines.filtered(lambda x, lot=lot: x.lot_id == lot).mapped(
                    "value_remaining"
                )
            )
            allocated = sum(self._get_allocations(lot=lot).mapped("allocated_amount"))
            self.assertAlmostEqual(
                allocated,
                remaining,
                delta=0.01,
                msg="Allocation mismatch on lot %s" % lot.name,
            )
        self.assertAlmostEqual(
            sum(self._get_allocations().mapped("allocated_amount")),
            sum(move_lines.mapped("value_remaining")),
            places=2,
        )

    def test_receipt_single_lot(self):
        __, move = self.create_picking("in", ["001"], ml_qty=5.0, price=10.0)
        layer = move.stock_valuation_layer_ids
        self.assertEqual(self._get_amounts_by_lot_name(layer), {"001": 50.0})
        self._assert_invariant()

    def test_receipt_multi_lot(self):
        __, move = self.create_picking("in", ["001", "002"], ml_qty=5.0, price=10.0)
        layer = move.stock_valuation_layer_ids
        self.assertEqual(
            self._get_amounts_by_lot_name(layer), {"001": 50.0, "002": 50.0}
        )
        self._assert_invariant()

    def test_delivery_single_lot(self):
        self.create_picking("in", ["001"], ml_qty=5.0, price=10.0)
        __, move_out = self.create_picking("out", ["001"], ml_qty=5.0)
        layer = move_out.stock_valuation_layer_ids
        self.assertEqual(self._get_amounts_by_lot_name(layer), {"001": -50.0})
        self._assert_invariant()

    def test_delivery_multi_lot_with_differing_costs(self):
        """The outgoing layer is an aggregate (-110 over 10 units): prorating it by
        quantity would charge -55 to each lot. The per-lot amounts have to come
        from the FIFO run, which knows lot 001 cost 10 and lot 002 cost 12."""
        self.create_picking("in", ["001"], ml_qty=5.0, price=10.0)
        self.create_picking("in", ["002"], ml_qty=5.0, price=12.0)
        __, move_out = self.create_picking("out", ["001", "002"], ml_qty=5.0)
        layer = move_out.stock_valuation_layer_ids
        self.assertEqual(layer.value, -110.0)
        self.assertEqual(
            self._get_amounts_by_lot_name(layer), {"001": -50.0, "002": -60.0}
        )
        self._assert_invariant()

    def test_delivery_with_force_fifo_lot(self):
        """The ledger charges the lot whose FIFO balance is consumed, which is what
        keeps it consistent with the valuation."""
        self.create_picking("in", ["001"], ml_qty=5.0, price=10.0)
        self.create_picking("in", ["002"], ml_qty=5.0, price=12.0)
        self.create_picking("out", ["002"], ml_qty=5.0)
        __, move_out = self.create_picking(
            "out", ["002"], ml_qty=5.0, force_lot_name="001"
        )
        layer = move_out.stock_valuation_layer_ids
        self.assertEqual(self._get_amounts_by_lot_name(layer), {"001": -50.0})
        self._assert_invariant()

    def test_landed_cost_on_partly_delivered_receipt(self):
        """A landed cost is scoped to its move and only lands on what is still in
        stock, so the lot that has left carries none of it."""
        __, move_in = self.create_picking("in", ["001", "002"], ml_qty=5.0, price=10.0)
        self.create_picking("out", ["001"], ml_qty=5.0)
        layer = self._create_value_only_layer(
            20.0, move=move_in, layer=move_in.stock_valuation_layer_ids
        )
        self.assertEqual(self._get_amounts_by_lot_name(layer), {"002": 20.0})
        self._assert_invariant()

    def test_price_difference(self):
        """A price difference layer carries no move, only the layer it corrects."""
        __, move_in = self.create_picking("in", ["001", "002"], ml_qty=5.0, price=10.0)
        self.create_picking("out", ["001"], ml_qty=5.0)
        layer = self._create_value_only_layer(
            20.0, layer=move_in.stock_valuation_layer_ids
        )
        self.assertEqual(self._get_amounts_by_lot_name(layer), {"002": 20.0})
        self._assert_invariant()

    def test_product_wide_revaluation(self):
        """With neither a move nor a parent layer, the scope is everything the
        product still holds in stock."""
        self.create_picking("in", ["001"], ml_qty=5.0, price=10.0)
        self.create_picking("in", ["002"], ml_qty=15.0, price=10.0)
        revaluation = self.env["stock.valuation.layer.revaluation"].create(
            {
                "product_id": self.product.id,
                "company_id": self.env.company.id,
                "added_value": 100.0,
                "reason": "Test product revaluation",
                "account_id": self._get_expense_account().id,
            }
        )
        revaluation.action_validate_revaluation()
        layer = self.env["stock.valuation.layer"].search(
            [("product_id", "=", self.product.id), ("quantity", "=", 0)]
        )
        self.assertEqual(
            self._get_amounts_by_lot_name(layer), {"001": 25.0, "002": 75.0}
        )
        self._assert_invariant()

    def test_lot_revaluation(self):
        """The wizard revalues a lot with an out/in pair of adjustments; both are
        allocated by the regular rules and net to the revalued amount."""
        self.create_picking("in", ["001", "002"], ml_qty=5.0, price=100.0)
        lot = self._get_lot("001")
        revaluation = self.env["stock.valuation.layer.revaluation"].create(
            {
                "product_id": self.product.id,
                "company_id": self.env.company.id,
                "lot_id": lot.id,
                "added_value": -10.0,
                "reason": "Test Revaluation Lot 001",
                "account_id": self._get_expense_account().id,
            }
        )
        revaluation.action_validate_revaluation()
        self.assertAlmostEqual(
            sum(self._get_allocations(lot=lot).mapped("allocated_amount")), 490.0
        )
        self._assert_invariant()

    def test_rounding(self):
        """Three equal shares of an amount that does not divide by three still add
        up to the layer value to the cent."""
        __, move = self.create_picking(
            "in", ["001", "002", "003"], ml_qty=1.0, price=3.335
        )
        layer = move.stock_valuation_layer_ids
        allocations = self._get_allocations(layer=layer)
        self.assertEqual(len(allocations), 3)
        self.assertEqual(sum(allocations.mapped("allocated_amount")), layer.value)
        self._assert_invariant()

    def test_backfill_is_idempotent(self):
        """The backfill must be safe to re-run and to overlap with a manual run,
        which is what lets the watermark be the only progress state."""
        __, move = self.create_picking("in", ["001", "002"], ml_qty=5.0, price=10.0)
        layer = move.stock_valuation_layer_ids
        self._get_allocations(layer=layer).unlink()
        layer._create_lot_allocations()
        self.assertEqual(len(self._get_allocations(layer=layer)), 2)
        layer._create_lot_allocations()
        self.assertEqual(len(self._get_allocations(layer=layer)), 2)
        self._assert_invariant()

    def test_backfill_watermark(self):
        layers = self.env["stock.valuation.layer"]
        self.assertEqual(layers._get_backfill_watermark(), 0)
        layers._set_backfill_watermark(42)
        self.assertEqual(layers._get_backfill_watermark(), 42)

    def test_balancing_pass(self):
        """Whatever the backfill could not compute exactly ends up in one visible
        adjustment row per lot, and the invariant holds again."""
        __, move = self.create_picking("in", ["001", "002"], ml_qty=5.0, price=10.0)
        lot = self._get_lot("001")
        # Stand in for an approximated history: the lot is under-allocated by 50.
        self._get_allocations(layer=move.stock_valuation_layer_ids, lot=lot).unlink()
        self.env["stock.valuation.layer"]._balance_lot_allocations()
        adjustment = self._get_allocations(lot=lot)
        self.assertEqual(len(adjustment), 1)
        self.assertEqual(adjustment.allocated_amount, 50.0)
        self.assertEqual(adjustment.description, "Opening allocation adjustment")
        self._assert_invariant()

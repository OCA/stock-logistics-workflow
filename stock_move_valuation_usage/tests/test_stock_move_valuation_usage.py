# 2026 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta

from odoo.tests import tagged

from odoo.addons.stock_account.tests.common import TestStockValuationCommon


@tagged("post_install", "-at_install")
class TestStockMoveValuationUsage(TestStockValuationCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.product_fifo

    def _assert_usages(self, out_move, expected):
        self.assertEqual(
            [
                (usage.src_stock_move_id, usage.quantity, usage.value)
                for usage in out_move.incoming_usage_ids.sorted("id")
            ],
            expected,
        )

    def test_01_stock_receipt(self):
        """Receive into stock and ship to the customer"""
        in_move = self._make_in_move(self.product, 1.0, 10.0)
        self.assertEqual(in_move.remaining_qty, 1.0)
        self.assertEqual(in_move.remaining_value, 10.0)
        out_move = self._make_out_move(self.product, 1.0)
        self.assertEqual(in_move.remaining_qty, 0.0)
        self.assertEqual(in_move.remaining_value, 0.0)
        self._assert_usages(out_move, [(in_move, 1.0, 10.0)])
        self.assertEqual(in_move.usage_ids.dest_stock_move_id, out_move)
        self.assertEqual(in_move.usage_quantity, 1.0)
        self.assertEqual(in_move.usage_value, 10.0)
        self.assertEqual(out_move.incoming_usage_quantity, 1.0)
        self.assertEqual(out_move.incoming_usage_value, 10.0)

    def test_02_drop_ship(self):
        """Drop shipment from vendor to customer"""
        move = self._make_dropship_move(self.product, 1.0, 10.0)
        self.assertTrue(move.is_dropship)
        self._assert_usages(move, [(move, 1.0, 10.0)])
        self.assertEqual(move.usage_ids.dest_stock_move_id, move)

    def test_03_revaluation_of_negative_fifo(self):
        """A receipt filling a negative stock is linked for the quantity it fills"""
        old_in_move = self._make_in_move(self.product, 2.0, 10.0)
        old_out_move = self._make_out_move(self.product, 2.0)
        in_move_1 = self._make_in_move(self.product, 4.0, 10.0)
        out_move = self._make_out_move(self.product, 10.0)
        self._assert_usages(out_move, [(in_move_1, 4.0, 40.0)])
        in_move_2 = self._make_in_move(self.product, 10.0, 8.0)
        self._assert_usages(out_move, [(in_move_1, 4.0, 40.0), (in_move_2, 6.0, 48.0)])
        self.assertEqual(out_move.value, -88.0)
        self.assertEqual(in_move_2.remaining_qty, 4.0)
        self._assert_usages(old_out_move, [(old_in_move, 2.0, 20.0)])

    def test_04_multiple_incoming_consumed_by_single_outgoing(self):
        in_move_1 = self._make_in_move(self.product, 1.0, 10.0)
        in_move_2 = self._make_in_move(self.product, 1.0, 8.0)
        out_move = self._make_out_move(self.product, 2.0)
        self._assert_usages(out_move, [(in_move_1, 1.0, 10.0), (in_move_2, 1.0, 8.0)])

    def test_05_outgoing_moves_validated_together(self):
        in_move_1 = self._make_in_move(self.product, 10.0, 10.0)
        in_move_2 = self._make_in_move(self.product, 10.0, 8.0)
        out_moves = self.env["stock.move"].create(
            [
                {
                    "product_id": self.product.id,
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.customer_location.id,
                    "picking_type_id": self.picking_type_out.id,
                    "product_uom_qty": qty,
                }
                for qty in (10.0, 5.0)
            ]
        )
        out_moves._action_confirm(merge=False)
        out_moves._action_assign()
        for move in out_moves:
            move.quantity = move.product_uom_qty
        out_moves.picked = True
        out_moves._action_done()
        out_move_1, out_move_2 = out_moves
        self._assert_usages(out_move_1, [(in_move_1, 10.0, 100.0)])
        self._assert_usages(out_move_2, [(in_move_2, 5.0, 40.0)])

    def test_06_revaluation_does_not_duplicate_usages(self):
        in_move = self._make_in_move(self.product, 10.0, 10.0)
        out_move = self._make_out_move(self.product, 4.0)
        with self.subTest("revaluation of the outgoing move"):
            out_move._set_value()
            self._assert_usages(out_move, [(in_move, 4.0, 40.0)])
        with self.subTest("FIFO price estimate"):
            self.assertEqual(self.product._get_fifo_value(2.0), 20.0)
            self.assertEqual(len(in_move.usage_ids), 1)

    def test_07_fifo_replay_updates_usages(self):
        in_move_1 = self._make_in_move(self.product, 5.0, 10.0)
        out_move = self._make_out_move(self.product, 5.0)
        self._assert_usages(out_move, [(in_move_1, 5.0, 50.0)])
        with self.subTest("cost update of the source move"):
            in_move_1.value_manual = 40.0
            self.assertEqual(out_move.value, -40.0)
            self._assert_usages(out_move, [(in_move_1, 5.0, 40.0)])
        with self.subTest("receipt backdated before the source move"):
            in_move_2 = self._make_in_move(self.product, 5.0, 6.0)
            in_move_2.date = in_move_1.date - timedelta(days=1)
            self.assertEqual(out_move.value, -30.0)
            self._assert_usages(out_move, [(in_move_2, 5.0, 30.0)])

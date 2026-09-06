# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import CommonStockLotTraceabilityCase


class TestStockLotTraceability(CommonStockLotTraceabilityCase):
    def test_produce_lots(self):
        """Test the Produced Lots/Serial Numbers field"""
        self.assertEqual(
            self.product1_lot1.produce_lot_ids, self.product2_lot1 + self.product3_lot1
        )
        self.assertEqual(self.product1_lot1.produce_lot_count, 2)
        self.assertEqual(self.product2_lot1.produce_lot_ids, self.product3_lot1)
        self.assertEqual(self.product2_lot1.produce_lot_count, 1)
        self.assertFalse(self.product3_lot1.produce_lot_ids)
        self.assertFalse(self.product3_lot1.produce_lot_count)

    def test_consume_lots(self):
        """Test the Consumed Lots/Serial Numbers field"""
        self.assertFalse(self.product1_lot1.consume_lot_ids)
        self.assertFalse(self.product1_lot1.consume_lot_count)
        self.assertEqual(self.product2_lot1.consume_lot_ids, self.product1_lot1)
        self.assertEqual(self.product2_lot1.consume_lot_count, 1)
        self.assertEqual(
            self.product3_lot1.consume_lot_ids, self.product1_lot1 + self.product2_lot1
        )
        self.assertEqual(self.product3_lot1.consume_lot_count, 2)

    def test_cache_invalidation(self):
        """Test that cache is invalidated when stock.move.line(s) are modified"""
        self.assertEqual(
            self.product1_lot1.produce_lot_ids, self.product2_lot1 + self.product3_lot1
        )
        self._do_stock_move(
            self.product2,
            self.product2_lot1,
            1,
            self.location_supplier,
            self.location_stock,
        )
        new_moves = self._do_manufacture_move(
            self.product3,
            self.product3_lot2,
            1,
            [(self.product2, self.product2_lot1, 10)],
        )
        self.assertEqual(
            self.product1_lot1.produce_lot_ids,
            self.product2_lot1 + self.product3_lot1 + self.product3_lot2,
        )
        new_moves[0].move_line_ids.consume_line_ids = [(5,)]
        self.assertEqual(
            self.product1_lot1.produce_lot_ids, self.product2_lot1 + self.product3_lot1
        )

    def test_action_view_produce_lots(self):
        """Test that no error is raised when calling this action"""
        self.assertIsInstance(self.product1_lot1.action_view_produce_lots(), dict)

    def test_action_view_consume_lots(self):
        """Test that no error is raised when calling this action"""
        self.assertIsInstance(self.product1_lot1.action_view_consume_lots(), dict)

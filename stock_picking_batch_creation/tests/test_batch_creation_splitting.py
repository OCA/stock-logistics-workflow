# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import ClusterPickingCommonFeatures


class TestBatchCreationSplitting(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_batch_creation_one_pick_move_over_the_limit(self):
        """Test splitting a picking when the first move exceed the weight limit."""
        self.pick2.action_cancel()
        self.pick3.action_cancel()
        # Keep the picking 1 with one line and product 1
        move = self.pick1.move_ids
        # And the weight of the move can not be accepted by the device
        max_weight = 9
        move_weight = move.product_id.weight * move.product_qty
        self.assertTrue(move_weight > max_weight)
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 2,
                "split_picking_exceeding_limits": True,
            }
        )
        device = self._create_device(
            "Device-A",
            min_volume=0,
            max_volume=0,
            max_weight=max_weight,
            nbr_bins=6,
            sequence=1,
        )
        self.make_picking_batch.stock_device_type_ids = device
        batch = self.make_picking_batch._create_batch()
        # There is no batch because the only picking could not be split
        self.assertFalse(batch)

    def test_batch_creation_move_over_the_limit_take_2nd_picking(self):
        """Test splitting a picking when the first move exceed the weight limit."""
        self.pick3.action_cancel()
        # Keep the picking 1 with one line and product 1
        move = self.pick1.move_ids
        # And the weight of the move can not be accepted by the device
        max_weight = 9
        move_weight = move.product_id.weight * move.product_qty
        self.assertTrue(move_weight > max_weight)
        # Get the picking to fit the limit
        self.pick2.move_ids.product_id.weight = 0.2
        # Force recomputation after changing the product weight
        self.pick2.move_ids._cal_move_weight()
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 2,
                "split_picking_exceeding_limits": True,
            }
        )
        device = self._create_device(
            "Device-A",
            min_volume=0,
            max_volume=0,
            max_weight=max_weight,
            nbr_bins=6,
            sequence=1,
        )
        self.make_picking_batch.stock_device_type_ids = device
        batch = self.make_picking_batch._create_batch()
        self.assertTrue(batch, "We should have a batch")
        self.assertTrue(self.pick2 in batch.picking_ids)
        self.assertTrue(batch.picking_ids, "We should have a picking in the batch")

    def test_batch_creation_splitting_by_number_of_lines(self):
        """Test splitting a picking when the number of lines exceed the limit."""
        self.pick1.action_cancel()
        self.pick2.action_cancel()
        # Keep the picking 3
        self._add_product_to_picking(self.pick3, self.p3)
        self._add_product_to_picking(self.pick3, self.p4)
        # And now it has 4 lines
        self.make_picking_batch.write({"maximum_number_of_preparation_lines": 2})
        self.make_picking_batch.write({"split_picking_exceeding_limits": True})
        device = self._create_device("Test", 0.0, 0.0, 0.0, 20, 1)
        self.make_picking_batch.stock_device_type_ids = device
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(self.pick3 in batch.picking_ids)
        self.assertTrue(batch, "We should have a batch")
        self.assertTrue(batch.picking_ids, "We should have a picking in the batch")
        self.assertEqual(len(batch.picking_ids.move_line_ids), 2)

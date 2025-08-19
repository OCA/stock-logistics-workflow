# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, RecordCapturer

from ..exceptions import (
    NoPickingCandidateError,
    NoSuitableDeviceError,
    PickingCandidateNumberLineExceedError,
)
from .common import ClusterPickingCommonFeatures


class TestClusteringConditions(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p5 = cls._create_product("Unittest P5", 1, 4, 1, 1)

    def test_device_with_one_bin(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3
        Test case: We have 3 devices possibles (device1, device2, device3),
        ordered following sequence: device3, device2, device1.
        The first picking will be pick3 (higher priority) and its volume is
        is 30m3. -> device3 is the device to use (min 30m3, max 100m3)

        Device3 has 1 bin -> the batch should only contain pick3
        """
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.device3, batch.picking_device_id)
        self.assertEqual(self.pick3, batch.picking_ids)

    def test_device_with_several_bins_volume_0_group_per_partner(self):
        """
        Got a selected picking with volume == 0
        Enable grouping per partner

        Ensure we can create batch
        """
        product = self._create_product("Without volume", 0.0, 0.0, 0.0, 0.0)
        self._set_quantity_in_stock(self.stock_location, product)
        self._create_picking_pick_and_assign(self.picking_type_1.id, 0, product)
        device = self._create_device("Test", 0.0, 0.0, 200.0, 20, 1)
        self.make_picking_batch.stock_device_type_ids = device
        self.make_picking_batch.group_pickings_by_partner = True
        self.make_picking_batch._create_batch()

    def test_put_3_pickings_in_one_cluster(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3
            pick1: 1 line
            pick2: 1 line
            pick3: 3 lines
        Test case:
            Add a line to pick3
            Create a new picking with 2 lines
            Set the maximum number of preparation lines to 6 on the wizard.
            Create a new batch where device3 will be used since the first pick
            to prepare is pick3 and its volume is 30m3. -> device3 is the device
        Expected result:
            The batch should contain pick3, pick2 and pick1 but not the new picking
            In this test case, only the number of lines is taken into account.
            The sum of lines for pick3, pick1, pick1 is (3 + 1 + 1) = 5
            The maximum number of preparation lines is 6.
            The new picking is not added to the batch since its number of lines is 2.
        """
        self._set_quantity_in_stock(self.stock_location, self.p5)
        self.p1.write(
            {
                "volume": 5.0,
                "product_length": 5,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "volume": 5.0,
                "product_length": 5,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self._add_product_to_picking(self.pick3, self.p5)
        self.make_picking_batch.write({"maximum_number_of_preparation_lines": 6})

        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1 | self.p5
        )
        self.device3.nbr_bins = 60
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.device3, batch.picking_device_id)
        self.assertEqual(self.pick3 | self.pick2 | self.pick1, batch.picking_ids)

    def test_no_device_for_clustering(self):
        """
        In this test we set the volume of all the products to 400m3.
        Therefore, no device can be used to prepare the batch.
        """
        self.p1.write(
            {
                "product_length": 400,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "product_length": 400,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        # since the volume is computed at picking creation or update, force
        # the recomputation
        (self.pick1 | self.pick2 | self.pick3).mapped("move_ids")._compute_volume()
        batch = self.make_picking_batch._create_batch(raise_if_not_possible=False)
        self.assertFalse(batch)
        message = "No device found for batch picking."
        with self.assertRaises(NoSuitableDeviceError) as cm:
            self.make_picking_batch._create_batch(raise_if_not_possible=True)
            self.assertEqual(cm.exception, message)

        # Display picking names in exception
        self.make_picking_batch.add_picking_list_in_error = True

        with self.assertRaises(NoSuitableDeviceError) as cm:
            self.make_picking_batch._create_batch(raise_if_not_possible=True)
        self.assertIn(
            self.pick1.name,
            repr(cm.exception),
        )

    def test_one_picking_on_another_device(self):
        """
        In this test, we set the volume of all the products to 10m3 for the
        existing pickings and 120m3 for a new picking.
        The new volume set on the existing picking will lead to the use
        of the device1 (min 10m3, max 50m3) since the volume of the first
        picking (pick3) to prepare is 10m3.
        The new picking will not be part of this batch since the volume of
        the new picking is 120m3 and the device1 can only prepare 50m3.
        """
        self.p1.write(
            {
                "volume": 10.0,
                "product_length": 10,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "volume": 10.0,
                "product_length": 10,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p5.write(
            {
                "volume": 120.0,
                "product_length": 120,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self._set_quantity_in_stock(self.stock_location, self.p5)
        self.device1.write({"nbr_bins": 8})
        self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p5, priority="0"
        )
        self.picks.mapped("move_ids")._compute_volume()
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.device1, batch.picking_device_id)
        self.assertEqual(self.pick3 | self.pick2 | self.pick1, batch.picking_ids)

    def test_put_2_pickings_with_volume_zero_in_one_cluster(self):
        """2 products don't have a volume :
        they should still occupy at least one bin each"""
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume null devices",
                "min_volume": 0,
                "max_volume": 200,
                "max_weight": 200,
                "nbr_bins": 6,
                "sequence": 50,
            }
        )
        make_picking_batch_volume_zero = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [(4, device.id)],
                "maximum_number_of_preparation_lines": 6,
            }
        )
        self.p1.write(
            {
                "product_length": 0,
                "product_height": 0,
                "product_width": 0,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "product_length": 0,
                "product_height": 0,
                "product_width": 0,
                "weight": 1,
            }
        )
        self.picks.mapped("move_ids")._compute_volume()
        self.assertEqual(0, self.pick1.volume)
        self.assertEqual(0, self.pick2.volume)
        self.assertEqual(0, self.pick3.volume)
        batch = make_picking_batch_volume_zero._create_batch()
        self.assertEqual(device, batch.picking_device_id)
        self.assertEqual(self.pick3 | self.pick2 | self.pick1, batch.picking_ids)

        # All picks have a volume of 0 : they should each occupy one bin
        self.assertEqual(batch.batch_nbr_bins, 3)

    def test_user_propagates_on_pickings(self):
        batch = self.make_picking_batch._create_batch()
        self.assertTrue(batch.picking_ids)
        self.assertEqual(batch.user_id.id, self.env.user.id)
        for pick in batch.picking_ids:
            self.assertEqual(pick.user_id.id, self.env.user.id)

        # remove user_id from batch
        batch.user_id = False
        for pick in batch.picking_ids:
            self.assertFalse(pick.user_id)

    def test_several_pickings_one_partner_one_bin_occupied(self):
        self.device1.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 300})
        self.p1.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 20,
                "group_pickings_by_partner": True,
            }
        )
        self.picks.mapped("move_ids")._compute_volume()
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.pick1 | self.pick2 | self.pick3, batch.picking_ids)
        self.assertEqual(batch.batch_nbr_bins, 1)

    def test_several_pickings_one_partner_two_bin_occupied(self):
        self.device3.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 300})
        self.p1.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "product_length": 35,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 20,
                "group_pickings_by_partner": True,
            }
        )

        self.picks.mapped("move_ids")._compute_volume()
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.pick1 | self.pick2 | self.pick3, batch.picking_ids)
        self.assertEqual(batch.batch_nbr_bins, 2)

    def test_several_pickings_two_partner_two_bin_occupied(self):
        self.device1.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 300})
        self.p1.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        partner2 = self.env["res.partner"].create(
            {"name": "other partner", "ref": "98098769876"}
        )
        pick_new_partner = self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1, partner=partner2
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 20,
                "group_pickings_by_partner": True,
            }
        )

        self.picks.mapped("move_ids")._compute_volume()
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(
            self.pick1 | self.pick2 | self.pick3 | pick_new_partner, batch.picking_ids
        )
        self.assertEqual(batch.batch_nbr_bins, 2)

    def test_several_pickings_one_partner_volume_outreached_on_one_picking(self):
        self.p1.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p5.write(
            {
                "product_length": 200,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )

        self._set_quantity_in_stock(self.stock_location, self.p5)
        self.device1.write({"nbr_bins": 8, "min_volume": 0, "max_volume": 30})
        self._create_picking_pick_and_assign(self.picking_type_1.id, products=self.p5)
        another_pick = self._create_picking_pick_and_assign(
            self.picking_type_1.id, products=self.p1 | self.p2
        )
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 10,
                "group_pickings_by_partner": True,
            }
        )
        self.picks.mapped("move_ids")._compute_volume()
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(
            self.pick1 | self.pick2 | self.pick3 | another_pick, batch.picking_ids
        )
        self.assertEqual(batch.batch_nbr_bins, 2)

    def test_device_with_one_bin_group_by_partners_product_volume_null(self):
        """By default when pick are grouped by partner into the batch, if no
        volume is set on the picking, we consider that the volume is
        the volume of one device bin."""
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume null devices and one bin",
                "min_volume": 0,
                "max_volume": 200,
                "max_weight": 200,
                "nbr_bins": 1,
                "sequence": 50,
            }
        )
        wiz = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [(4, device.id)],
                "group_pickings_by_partner": True,
                "maximum_number_of_preparation_lines": 6,
            }
        )
        self.p1.write(
            {"product_length": 0, "product_height": 0, "product_width": 0, "weight": 1}
        )
        self.p2.write(
            {"product_length": 0, "product_height": 0, "product_width": 0, "weight": 1}
        )
        self.picks.mapped("move_ids")._compute_volume()
        batch = wiz._create_batch()
        self.assertEqual(self.pick3, batch.picking_ids)

    def test_pickings_with_different_priority(self):
        self._set_quantity_in_stock(self.stock_location, self.p5)
        self._create_picking_pick_and_assign(self.picking_type_1.id, products=self.p5)
        (self.pick1 | self.pick2).write({"priority": "1"})
        self.pick3.write({"priority": "0"})
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 10,
                "restrict_to_same_priority": True,
            }
        )
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.pick1 | self.pick2, batch.picking_ids)
        batch2 = self.make_picking_batch._create_batch()
        self.assertEqual(self.pick3, batch2.picking_ids)

    def test_pickings_with_different_partners(self):
        partner1 = self.env["res.partner"].create({"name": "partner 1"})
        partner2 = self.env["res.partner"].create({"name": "partner 2"})
        self._set_quantity_in_stock(self.stock_location, self.p5)
        self._create_picking_pick_and_assign(self.picking_type_1.id, products=self.p5)
        (self.pick1 | self.pick2).write({"partner_id": partner1.id})
        self.pick3.write({"partner_id": partner2.id})
        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 10,
                "restrict_to_same_partner": True,
            }
        )
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.pick3, batch.picking_ids)
        batch2 = self.make_picking_batch._create_batch()
        self.assertEqual(self.pick1 | self.pick2, batch2.picking_ids)

    def test_picking_split_with_maximum_number_of_lines_exceed(self):
        # pick 3 has 2 lines
        # create a batch picking with maximum number of lines = 1
        self.pick1.action_cancel()
        self.pick2.action_cancel()

        self.make_picking_batch.write(
            {
                "maximum_number_of_preparation_lines": 1,
                "split_picking_exceeding_limits": False,
            }
        )
        with self.assertRaises(PickingCandidateNumberLineExceedError):
            self.make_picking_batch._create_batch(raise_if_not_possible=True)
        self.make_picking_batch.split_picking_exceeding_limits = True
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            batch = self.make_picking_batch._create_batch()
            new_pickings = rc.records
        self.assertEqual(new_pickings, batch.picking_ids)
        self.assertEqual(len(batch.move_line_ids), 1)

    def test_device_with_one_bin_create_action(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3
        Test case: We have 3 devices possibles (device1, device2, device3),
        ordered following sequence: device3, device2, device1.
        The first picking will be pick3 (higher priority) and its volume is
        is 30m3. -> device3 is the device to use (min 30m3, max 100m3)

        Device3 has 1 bin -> the batch should only contain pick3
        """
        batch_action = self.make_picking_batch.create_batch()
        batch = self.env["stock.picking.batch"].browse(batch_action.get("res_id"))
        self.assertEqual(self.device3, batch.picking_device_id)
        self.assertEqual(self.pick3, batch.picking_ids)

    def test_device_with_one_bin_create_action_no_picking(self):
        """
        Cancel all pickings

        No picking candidate error should be raised
        """
        self.picks.action_cancel()
        with self.assertRaises(NoPickingCandidateError):
            self.make_picking_batch.create_batch()

    def test_put_2_pickings_with_volume_in_one_cluster(self):
        """2 products have a volume :
        they should still occupy at least one bin each"""
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume devices",
                "min_volume": 0,
                "max_volume": 200,
                "max_weight": 200,
                "nbr_bins": 6,
                "sequence": 50,
            }
        )
        make_picking_batch_volume_zero = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [(4, device.id)],
                "maximum_number_of_preparation_lines": 6,
            }
        )
        self.p1.write(
            {
                "product_length": 1,
                "product_height": 1,
                "product_width": 1,
                "weight": 1,
            }
        )
        self.p2.write(
            {
                "product_length": 1,
                "product_height": 2,
                "product_width": 3,
                "weight": 1,
            }
        )
        self.picks.mapped("move_ids")._compute_volume()
        self.assertEqual(1.0, self.pick1.volume)
        self.assertEqual(6.0, self.pick2.volume)
        self.assertEqual(7.0, self.pick3.volume)
        batch = make_picking_batch_volume_zero._create_batch()
        self.assertEqual(device, batch.picking_device_id)
        self.assertEqual(self.pick3 | self.pick2 | self.pick1, batch.picking_ids)

        # All picks have a volume of 0 : they should each occupy one bin
        self.assertEqual(batch.batch_nbr_bins, 3)

    def test_changing_device_constraints(self):
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume devices",
                "min_volume": 0,
                "max_volume": 200,
                "max_weight": 200,
                "nbr_bins": 6,
                "sequence": 50,
            }
        )
        self.assertEqual(device.user_max_volume, 200.0)
        self.assertEqual(device.user_min_volume, 0.0)
        self.assertEqual(device.user_max_weight, 200.0)

        device.write(
            {
                "min_volume": 100.0,
            }
        )
        self.assertEqual(device.user_min_volume, 100.0)
        self.assertAlmostEqual(device.volume_per_bin, 33.33, places=2)

        # Test user interface
        with Form(device) as device_form:
            device_form.user_min_volume = 0.0
        device = device_form.save()
        self.assertEqual(device.min_volume, 0.0)

        with Form(device) as device_form:
            device_form.user_min_volume = 10.0
        device = device_form.save()
        self.assertEqual(device.min_volume, 10.0)

        with Form(device) as device_form:
            device_form.user_max_volume = 300.0
        device = device_form.save()
        self.assertEqual(device.max_volume, 300.0)

        with Form(device) as device_form:
            device_form.user_max_volume = 0.0
        device = device_form.save()
        self.assertEqual(device.max_volume, 0.0)

        with Form(device) as device_form:
            device_form.user_max_weight = 0.0
        device = device_form.save()
        self.assertEqual(device.max_weight, 0.0)

        with Form(device) as device_form:
            device_form.user_max_weight = 100.0
        device = device_form.save()
        self.assertEqual(device.max_weight, 100.0)

    def test_picking_split_with_weight_exceed(self):
        # pick 3 has 2 lines
        # we will set a weight by line under the maximum weight of the device
        # but the total weight of the picking will exceed the maximum weight of the
        # device when the batch is created, the picking 3 should be split and the batch
        # should contain only pick3 with 1 line

        self.pick1.action_cancel()
        self.pick2.action_cancel()
        self.assertEqual(len(self.pick3.move_line_ids), 2)
        max_weight = 200
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume null devices and one bin",
                "min_volume": 0,
                "max_volume": 200,
                "max_weight": max_weight,
                "nbr_bins": 1,
                "sequence": 50,
            }
        )

        self.make_picking_batch.write(
            {
                "split_picking_exceeding_limits": False,
                "stock_device_type_ids": [(6, 0, [device.id])],
            }
        )
        self.pick3.move_ids.product_id.weight = max_weight - 1
        self.pick3.move_ids._cal_move_weight()
        with self.assertRaises(NoSuitableDeviceError):
            self.make_picking_batch._create_batch(raise_if_not_possible=True)
        self.make_picking_batch.split_picking_exceeding_limits = True
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            batch = self.make_picking_batch._create_batch()
            new_pickings = rc.records
        self.assertEqual(new_pickings, batch.picking_ids)
        self.assertEqual(len(batch.move_line_ids), 1)

    def test_picking_split_with_volume_exceed(self):
        # pick 3 has 2 lines
        # we will set a volume by line under the maximum volume of the device
        # but the total volume of the picking will exceed the maximum volume of the
        # device when the batch is created, the picking 3 should be split and the batch
        # should contain only pick3 with 1 line

        self.pick1.action_cancel()
        self.pick2.action_cancel()
        self.assertEqual(len(self.pick3.move_line_ids), 2)

        max_volume = 200
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume null devices and one bin",
                "min_volume": 0,
                "max_volume": max_volume,
                "max_weight": 300,
                "nbr_bins": 1,
                "sequence": 50,
            }
        )

        self.make_picking_batch.write(
            {
                "split_picking_exceeding_limits": False,
                "stock_device_type_ids": [(6, 0, [device.id])],
            }
        )
        # each product has a volume of 120
        self.pick3.move_ids.product_id.write(
            {
                "product_length": 12,
                "product_height": 5,
                "product_width": 2,
            }
        )
        self.pick3.move_ids._compute_volume()
        with self.assertRaises(NoSuitableDeviceError):
            self.make_picking_batch._create_batch(raise_if_not_possible=True)
        self.make_picking_batch.split_picking_exceeding_limits = True
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            batch = self.make_picking_batch._create_batch()
            new_pickings = rc.records
        self.assertEqual(new_pickings, batch.picking_ids)
        self.assertEqual(len(batch.move_line_ids), 1)

    def test_picking_split_priority(self):
        # We ensure than even if a picking with a higher priority has a volume
        # exceeding the device capacity, it will be split and processed first
        # if the split_picking_exceeding_limits is set to True
        # the processing order for picks of type 1 will be:
        # pick3 (priority), pick1 (lower id), pick2
        self.assertEqual(len(self.pick3.move_line_ids), 2)

        max_volume = 200
        device = self.env["stock.device.type"].create(
            {
                "name": "test volume null devices and one bin",
                "min_volume": 0,
                "max_volume": max_volume,
                "max_weight": 300,
                "nbr_bins": 1,
                "sequence": 50,
            }
        )

        self.make_picking_batch.write(
            {
                "split_picking_exceeding_limits": False,
                "stock_device_type_ids": [(6, 0, [device.id])],
            }
        )
        # each product has a volume of 120
        self.pick3.move_ids.product_id.write(
            {
                "product_length": 12,
                "product_height": 5,
                "product_width": 2,
            }
        )
        self.pick3.move_ids._compute_volume()

        # since pick3 exceeds the device capacity and
        # the split_picking_exceeding_limits is set to False
        # the next picking to process should be pick1
        batch = self.make_picking_batch._create_batch()
        self.assertEqual(self.pick1, batch.picking_ids)

        batch.unlink()

        # if the split_picking_exceeding_limits is set to True.
        # then pick3 should be split and processed first
        self.make_picking_batch.split_picking_exceeding_limits = True
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            batch = self.make_picking_batch._create_batch()
            new_pickings = rc.records
        self.assertEqual(new_pickings, batch.picking_ids)

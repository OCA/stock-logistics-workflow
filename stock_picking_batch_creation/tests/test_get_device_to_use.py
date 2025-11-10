# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from .common import ClusterPickingCommonFeatures


class TestGetDeviceToUse(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_device_to_use_00(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3
        Test case: We have 3 devices possibles (device1, device2, device3),
        ordered following sequence: device3, device2, device1.
        Expected Result: "device3" should be the device to use since it's the one
        that fits for pick3, the first pick to process according to priority.
        (min volume is 30m3 and max volume is 100m3)
        """
        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device3)

    def test_get_device_to_use_01(self):
        """
        Data: we create 1 new product with big volume in zone 1
        Test case: We have 3 devices possibles (device1, device2, device3),
        ordered following sequence: device3, device2, device1.
        The volume of the products is higher than the max volume of device3
        but not device2 which is next in line
        Expected Result: "device2" should be the device
        to use for this cluster since its
        max volume is 190m3
        """
        product_big_1 = self._create_product("Unittest P1 voluminous", 10, 100, 1, 1)
        self._set_quantity_in_stock(self.stock_location, product_big_1)
        self._add_product_to_picking(self.pick3, product_big_1)

        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device2)

    def test_get_device_to_use_no_matching_device(self):
        """Use case: There's no device that can handle the picking

        Data:
        We create a new product with a really big and heavy product in zone 1.

        Test case:
        We have 3 devices possibles (device1, device2, device3), ordered following
        sequence: device3, device2, device1.

        Expected Result:
        No device can be used to handle it, so another picking is selected.
        """
        product_big_1 = self._create_product("Unittest P1 big & heavy", 800, 80, 80, 80)
        self._set_quantity_in_stock(self.stock_location, product_big_1)
        self._add_product_to_picking(self.pick3, product_big_1)

        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [
                    Command.set(self.picking_type_1.ids),
                ],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device2.id),
                    Command.link(self.device3.id),
                ],
            }
        )

        self.assertFalse(
            make_picking_batch._compute_device_to_use(self.pick3),
            "No device can hold this picking",
        )

        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick1)

    def test_get_device_to_use_without_max_volume(self):
        """Use case: There's no max volume set, so it's unlimited

        Data:
        We create a new product with a really big volume in zone 1.
        We remove the max volume from device1.

        Test case:
        We have 3 devices possibles (device1, device2, device3), ordered following
        sequence: device3, device2, device1.

        Expected Result:
        device1 should be the device to use since it's the one with no max volume,
        effectively unlimited.
        """
        self.device1.max_volume = 0  # Effectively unlimited
        product_big_1 = self._create_product("Unittest P1 voluminous", 10, 800, 1, 1)
        self._set_quantity_in_stock(self.stock_location, product_big_1)
        self._add_product_to_picking(self.pick3, product_big_1)

        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [
                    Command.set(self.picking_type_1.ids),
                ],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device2.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device1)

    def test_get_device_to_use_without_max_weight(self):
        """Use case: There's no max weight set, so it's unlimited

        Data:
        We create a new product with a really big weight in zone 1.
        We remove the max weight from device2.
        We remove the min volume from device2 to not interfere (previously 70).

        Test case:
        We have 3 devices possibles (device1, device2, device3), ordered following
        sequence: device3, device2, device1.

        Expected Result:
        device2 should be the device to use since it's the one with no max weight,
        effectively unlimited.
        """
        self.device2.max_weight = 0  # Effectively unlimited
        self.device2.min_volume = 0  # No min_volume to not interfere
        product_big_1 = self._create_product("Unittest P1 heavy", 800, 1, 1, 1)
        self._set_quantity_in_stock(self.stock_location, product_big_1)
        self._add_product_to_picking(self.pick3, product_big_1)

        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [
                    Command.set(self.picking_type_1.ids),
                ],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device2.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device2)

    def test_get_device_to_use_filter_pickings(self):
        """
        Data: we create 1 new product with big volume in zone 1
        Test case: We have 3 devices possibles (device1, device2, device3),
        ordered following sequence: device3, device2, device1.
        The volume of the products is higher that the max volume
        of all devices and the product is added to the pick 3
        The first picking must be pick 1 (volume 10) with device 1 (min volume 5)
        (device 3 has a min volume of 30 and device 2 has a min volume of 70)
        """
        product_big_1 = self._create_product("Unittest P1 voluminous", 10, 10000, 1, 1)
        self._set_quantity_in_stock(self.stock_location, product_big_1)
        self._add_product_to_picking(self.pick3, product_big_1)

        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick1)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device1)

    def test_device_used_for_first_picking_splitting_00(self):
        """Check the last device is used for splitting the first picking.

        Default order is :: device3, device2, device1.
        The last device (device1) can not manage the only picking.
        So the picking will be split.

        """
        # Keep only one picking and a heavy one
        self.pick1.action_cancel()
        self.pick2.action_cancel()
        product_big_1 = self._create_product("Unittest P1 voluminous", 10, 100, 1, 1)
        self._set_quantity_in_stock(self.stock_location, product_big_1)
        self._add_product_to_picking(self.pick3, product_big_1)
        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "split_picking_exceeding_limits": True,
                # Add the device not in their default sort order
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        # A split picking has been created
        self.assertTrue(first_picking != self.pick3)

    def test_device_used_for_first_picking_splitting_01(self):
        """Check the last device is used for splitting the first picking.

        The last device (device2) can manage the only picking.
        So picking will not be split.

        """
        # Keep only one picking and a heavy one.
        self.pick1.action_cancel()
        self.pick2.action_cancel()
        product_big_1 = self._create_product("Unittest P1 voluminous", 10, 100, 1, 1)
        self._set_quantity_in_stock(self.stock_location, product_big_1)
        self._add_product_to_picking(self.pick3, product_big_1)
        # Set the device order
        self.device1.sequence = 10
        self.device3.sequence = 20
        self.device2.sequence = 30
        make_picking_batch = self.make_picking_batch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_1.id)],
                "split_picking_exceeding_limits": True,
                # Add the device not in their default sort order
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)

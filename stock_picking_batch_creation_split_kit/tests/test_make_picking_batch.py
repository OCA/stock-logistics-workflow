# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import RecordCapturer

from odoo.addons.stock_picking_batch_creation.tests.common import (
    ClusterPickingCommonFeatures,
)


class TestMakePickingBatch(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a kit product
        cls.product_leg = cls._create_product("Table Leg", 1, 10, 0.5, 0.5)
        cls.product_tabletop = cls._create_product("Table Top", 5, 20, 5, 0.5)
        cls.product_table = cls._create_product("Table", 0, 0, 0, 0, is_storable=False)
        # Bill of material
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product_table.id,
                "product_tmpl_id": cls.product_table.product_tmpl_id.id,
                "product_qty": 1,
                "type": "phantom",
                "bom_line_ids": [
                    Command.create(
                        {"product_id": cls.product_leg.id, "product_qty": 4}
                    ),
                    Command.create(
                        {"product_id": cls.product_tabletop.id, "product_qty": 1}
                    ),
                ],
            }
        )
        # Some initial stocks
        cls._set_quantity_in_stock(cls.stock_location, cls.product_leg)
        cls._set_quantity_in_stock(cls.stock_location, cls.product_tabletop)
        # Create some pickings with the kits
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Kits Picking type",
                "code": "internal",
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": cls.location_out.id,
                "color": 7,
                "sequence": 4,
                "sequence_id": cls.warehouse_1.pick_type_id.sequence_id.id,
                "sequence_code": "test_kits",
            }
        )
        cls.pick1 = cls._create_picking_pick_and_assign(
            cls.picking_type.id, products=cls.product_table
        )
        cls.pick2 = cls._create_picking_pick_and_assign(
            cls.picking_type.id, priority="1", products=cls.product_table + cls.p1
        )
        # Group all pickings
        cls.picks = cls.pick1 | cls.pick2
        # Configure devices limits mode
        cls.devices = cls.device1 | cls.device2 | cls.device3
        cls.devices.split_mode = "kit_quantity"
        cls.devices.nbr_bins = 1
        # Create the batch wizard
        cls.make_picking_batch = cls.makePickingBatch.create(
            {
                "user_id": cls.env.user.id,
                "picking_type_ids": [Command.set(cls.picking_type.ids)],
                "stock_device_type_ids": [Command.set(cls.devices.ids)],
                "split_picking_exceeding_limits": True,
                # disable lock: All tests are run in the same transaction
                "picking_locking_mode": False,
            }
        )

    def test_device_with_one_bin(self):
        """
        Data:
        - 2 picks of given type
        - Total of 2 kits (2 * 5 components) + 1 simple product

        Test case:
        - We have 3 devices possibles (device1, device2, device3),
          ordered following sequence: device3, device2, device1.

        The first picking will be pick2 (higher priority) and its volume is
        is 65m3. -> device3 is the device to use (min 30m3, max 100m3)

        Device3 has 1 bin -> the batch should split the picking and contain
        only the kit.
        """
        # Prepare the batch
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            batch = self.make_picking_batch._create_batch()
            new_pickings = rc.records
        self.assertEqual(
            batch.picking_device_id, self.device3, "device3 should be used"
        )
        self.assertEqual(len(new_pickings), 1, "New picking created")
        self.assertEqual(
            new_pickings,
            batch.picking_ids,
            "New picking is the one used in the batch",
        )
        self.assertEqual(len(new_pickings.move_ids), 2)
        self.assertEqual(
            new_pickings.move_ids.product_id,
            (self.product_tabletop + self.product_leg),
            "New picking should contain the kit",
        )

    def test_device_with_two_bins(self):
        """
        Data:
        - 2 picks of given type
        - Total of 2 kits (2 * 5 components) + 1 simple product

        Device3 has 2 bins -> no splitting needed.
        """
        self.device3.nbr_bins = 3
        self.make_picking_batch.stock_device_type_ids = [Command.set(self.device3.ids)]
        # Prepare the batch
        with RecordCapturer(self.env["stock.picking"], []) as rc:
            batch = self.make_picking_batch._create_batch()
            new_pickings = rc.records
        self.assertEqual(
            batch.picking_device_id, self.device3, "device3 should be used"
        )
        self.assertFalse(new_pickings, "No new picking created")
        self.assertEqual(batch.picking_ids, self.pick2)

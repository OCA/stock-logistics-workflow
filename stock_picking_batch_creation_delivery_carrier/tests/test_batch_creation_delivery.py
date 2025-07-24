# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_picking_batch_creation.tests.common import (
    ClusterPickingCommonFeatures,
)


class TestClusteringConditions(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_delivery = cls.env["product.product"].create(
            {
                "name": "Delivery Batchs",
                "type": "service",
            }
        )
        cls.delivery_carrier_id = cls.env["delivery.carrier"].create(
            {
                "name": "Test for Batchs",
                "product_id": cls.product_delivery.id,
            }
        )
        # Ensure there is always bins
        cls.make_picking_batch.stock_device_type_ids.nbr_bins = 10

    def test_picking_with_delivery_carrier(self):
        # pick 3 has 2 lines
        # assign delivery carrier to pick1 and pick3
        # make a batch for that carrier
        self.pick1.carrier_id = self.delivery_carrier_id
        self.pick3.carrier_id = self.delivery_carrier_id

        self.make_picking_batch.write(
            {
                "delivery_carrier_id": self.delivery_carrier_id.id,
            }
        )
        batch = self.make_picking_batch._create_batch()
        self.assertEqual((self.pick3 | self.pick1), batch.picking_ids)
        self.assertEqual(len(batch.move_line_ids), 3)

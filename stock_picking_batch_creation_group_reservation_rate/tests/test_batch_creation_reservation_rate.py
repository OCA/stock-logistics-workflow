# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError

from odoo.addons.stock_picking_batch_creation.tests.common import (
    ClusterPickingCommonFeatures,
)


class TestClusteringConditions(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env["procurement.group"].create(
            {
                "name": "Group Test",
            }
        )
        cls.type_group = cls.env["stock.picking.type.group"].create(
            {
                "name": "PICK group",
            }
        )
        cls.type_group.picking_type_ids |= cls.pick3.picking_type_id
        # Ensure there is always bins
        cls.make_picking_batch.stock_device_type_ids.nbr_bins = 10
        # Assign group to all pickings
        cls.picks.move_ids.group_id = cls.group
        cls.picks._compute_type_group_reservation_rate()

    def test_picking_with_reservation_rate_range_no_picking(self):
        self.make_picking_batch.group_reservation_rate = True
        self.make_picking_batch.group_reservation_rate_max = 90.0
        batch = self.make_picking_batch._create_batch()
        self.assertFalse(batch.picking_ids)

    def test_picking_with_reservation_rate_range(self):
        self.make_picking_batch.group_reservation_rate = True
        batch = self.make_picking_batch._create_batch()
        self.assertEqual((self.pick1 | self.pick2 | self.pick3), batch.picking_ids)

    def test_picking_with_reservation_rate_range_constrains(self):
        self.make_picking_batch.group_reservation_rate = True
        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_max = 110.0

        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_max = -110.0

        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_min = -110.0

        self.make_picking_batch.group_reservation_rate_max = 90.0
        with self.assertRaises(ValidationError):
            self.make_picking_batch.group_reservation_rate_min = 100.0

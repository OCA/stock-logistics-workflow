# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import TransactionCase

from .common import OperationLossQuantityCommon


class TestWarehouseConfiguration(OperationLossQuantityCommon, TransactionCase):
    def test_warehouse_configuration(self):
        # Check loss location configuration
        self.assertTrue(self.warehouse.loss_location_id)
        self.assertEqual(
            self.warehouse.view_location_id, self.warehouse.loss_location_id.location_id
        )

        # Check loss picking type
        self.assertTrue(self.warehouse.loss_type_id)
        self.assertEqual(
            self.warehouse.loss_type_id.default_location_dest_id,
            self.warehouse.loss_location_id,
        )

        # Unset using loss feature
        self.warehouse.use_loss_picking = False
        self.assertFalse(self.warehouse.loss_location_id.active)
        self.assertFalse(self.warehouse.loss_type_id.active)

# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from .common import OperationLossQuantityCommon


class TestWarehouseConfiguration(OperationLossQuantityCommon):
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

        # Check loss route
        route = self.warehouse.loss_route_id
        self.assertTrue(route.allow_quant_lock)
        self.assertEqual(len(route.rule_ids), 1)
        self.assertRecordValues(
            route.rule_ids,
            [
                {
                    "action": "pull",
                    "procure_method": "make_to_stock",
                    "location_src_id": self.warehouse.view_location_id.id,
                    "location_dest_id": self.warehouse.loss_location_id.id,
                    "picking_type_id": self.warehouse.loss_type_id.id,
                }
            ],
        )

        # Unset using loss feature
        self.warehouse.use_loss_picking = False
        self.assertFalse(self.warehouse.loss_location_id.active)
        self.assertFalse(self.warehouse.loss_type_id.active)
        self.assertFalse(self.warehouse.loss_route_id.active)

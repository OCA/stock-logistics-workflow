# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import users

from .common import TestStockCustomerDepositCommon


class TestStockWareHoseCustomerDeposit(TestStockCustomerDepositCommon):
    @users("stock_manager")
    def test_warehouse_activate_customer_deposit(self):
        """Create warehouse with use customer deposits, after deactivate and activate again."""
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse2",
                "code": "TST",
                "use_customer_deposits": True,
            }
        )
        # Check operation types
        self.assertTrue(warehouse.customer_deposit_type_id)
        operation_type = warehouse.customer_deposit_type_id
        self.assertRecordValues(
            operation_type,
            [
                {
                    "name": "Customer Deposit",
                    "code": "internal",
                    "use_create_lots": False,
                    "use_existing_lots": True,
                    "assign_owner": True,
                    "default_location_src_id": warehouse.lot_stock_id.id,
                    "default_location_dest_id": warehouse.lot_stock_id.id,
                    "show_reserved": False,
                    "show_operations": True,
                    "sequence_code": "DEPOSIT",
                    "barcode": "TST-DEPOSIT",
                },
            ],
        )
        # Check sequences
        self.assertTrue(warehouse.customer_deposit_type_id.sequence_id)
        self.assertRecordValues(
            warehouse.customer_deposit_type_id.sequence_id,
            [
                {
                    "name": "Test Warehouse2 Sequence Customer Deposit",
                    "prefix": "TST/DEPOSIT/",
                },
            ],
        )
        # Check route
        self.assertTrue(warehouse.customer_deposit_route_id)
        route = warehouse.customer_deposit_route_id
        self.assertRecordValues(
            warehouse.customer_deposit_route_id,
            [
                {
                    "name": "Test Warehouse2: Customer Deposit",
                    "product_categ_selectable": False,
                    "warehouse_selectable": False,
                    "product_selectable": False,
                    "sale_selectable": True,
                }
            ],
        )
        # Check rules
        self.assertTrue(len(warehouse.customer_deposit_route_id.rule_ids), 2)
        self.assertRecordValues(
            warehouse.customer_deposit_route_id.rule_ids,
            [
                {
                    "location_src_id": warehouse.lot_stock_id.id,
                    "location_dest_id": self.customer_location.id,
                    "picking_type_id": operation_type.id,
                    "action": "pull",
                },
            ],
        )
        warehouse.write({"use_customer_deposits": False})
        self.assertFalse(warehouse.customer_deposit_type_id.active)
        self.assertFalse(warehouse.customer_deposit_route_id.active)
        warehouse.write({"use_customer_deposits": True})
        self.assertTrue(operation_type.active)
        self.assertTrue(route.active)

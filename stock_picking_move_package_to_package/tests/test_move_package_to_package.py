# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestStockPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.ResCompany = cls.env["res.company"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.StockPackage = cls.env["stock.quant.package"]
        cls.StockQuant = cls.env["stock.quant"]
        cls.Product = cls.env["product.product"]
        cls.PackageLevel = cls.env["stock.package_level"]
        cls.StockMoveLine = cls.env["stock.move.line"]
        cls.company = cls.ResCompany.create({"name": "Company A"})
        cls.user_demo = cls.env["res.users"].create(
            {
                "login": "firstnametest",
                "name": "User Demo",
                "email": "firstnametest@example.org",
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                    (4, cls.env.ref("stock.group_stock_user").id),
                ],
            }
        )
        group_stock_multi_locations = cls.env.ref("stock.group_stock_multi_locations")
        group_stock_adv_location = cls.env.ref("stock.group_adv_location")
        cls.user_demo.write(
            {
                "company_id": cls.company.id,
                "company_ids": [(4, cls.company.id)],
                "groups_id": [
                    (4, group_stock_multi_locations.id, 0),
                    (4, group_stock_adv_location.id, 0),
                ],
            }
        )
        cls.stock_location = (
            cls.env["stock.location"]
            .sudo()
            .search(
                [("name", "=", "Stock"), ("company_id", "=", cls.company.id)], limit=1
            )
        )
        cls.warehouse = cls.stock_location.warehouse_id
        cls.warehouse.write({"reception_steps": "two_steps"})
        cls.input_location = cls.warehouse.wh_input_stock_loc_id
        cls.in_type = cls.warehouse.in_type_id
        cls.in_type.write({"show_entire_packs": True})
        cls.int_type = cls.warehouse.int_type_id
        cls.int_type.write({"show_entire_packs": True})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    def test_move_package_to_package_no_tracking_products(self):
        # Create a products
        product1 = self.Product.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "default_code": "TEST_PROD1",
                "tracking": "none",
            }
        )
        product2 = self.Product.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "default_code": "TEST_PROD2",
                "tracking": "none",
            }
        )

        # Create a IN picking product 1
        incoming_picking1 = (
            self.StockPicking.with_context(default_company_id=self.company.id)
            .with_user(self.user_demo)
            .create(
                {
                    "location_dest_id": self.input_location.id,
                    "picking_type_id": self.in_type.id,
                }
            )
        )
        self.StockMoveLine.create(
            {
                "product_id": product1.id,
                "product_uom_id": self.uom_unit.id,
                "qty_done": 3.0,
                "picking_id": incoming_picking1.id,
            }
        )
        # Put in pack, in order to use this package for testing the move packages logic
        incoming_picking1.action_put_in_pack()
        incoming_picking1.action_confirm()
        incoming_picking1.button_validate()

        internal_picking1 = self.StockPicking.search(
            [("origin", "=", incoming_picking1.name)]
        )
        package_level1 = internal_picking1.package_level_ids
        package_level1.write({"is_done": True})
        internal_picking1.action_confirm()
        internal_picking1.button_validate()
        package1 = package_level1.package_id

        # Create a IN picking product 2
        incoming_picking2 = (
            self.StockPicking.with_context(default_company_id=self.company.id)
            .with_user(self.user_demo)
            .create(
                {
                    "location_dest_id": self.input_location.id,
                    "picking_type_id": self.in_type.id,
                }
            )
        )
        self.StockMoveLine.create(
            {
                "product_id": product2.id,
                "product_uom_id": self.uom_unit.id,
                "qty_done": 2.0,
                "picking_id": incoming_picking2.id,
            }
        )
        # Put in pack, in order to use this package for testing the move packages logic
        incoming_picking2.action_put_in_pack()
        incoming_picking2.action_confirm()
        incoming_picking2.button_validate()

        internal_picking2 = self.StockPicking.search(
            [("origin", "=", incoming_picking2.name)]
        )

        package_level2 = internal_picking2.package_level_ids
        package2 = package_level2.package_id

        # Move package2 to package1
        package_level2.package_dest_id = package1
        self.assertTrue(package_level2.is_done)

        # Validate the picking
        internal_picking2.action_confirm()
        internal_picking2.button_validate()

        # Test if only one quant is created per line
        quant1 = self.StockQuant.search(
            [
                ("product_id", "=", product1.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        quant2 = self.StockQuant.search(
            [
                ("product_id", "=", product2.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        self.assertEqual(len(quant1), 1)
        self.assertEqual(len(quant2), 1)

        # Test if all pickings are done
        self.assertEqual(incoming_picking1.state, "done")
        self.assertEqual(incoming_picking2.state, "done")
        self.assertEqual(internal_picking1.state, "done")
        self.assertEqual(internal_picking2.state, "done")

        # Test if the source package is empty
        self.assertEqual(len(package2.quant_ids), 0)

        # Test if the destination package contains the content from the source package
        self.assertEqual(len(package1.quant_ids), 2)
        self.assertIn(
            product1,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            product2,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )

        # Check the available product qty of product1 and product2 after the operations
        self.assertEqual(
            product1.qty_available, 3.0, "Total product quantity is not as expected."
        )
        self.assertEqual(
            product2.qty_available, 2.0, "Total product quantity is not as expected."
        )

    def test_move_package_to_package_with_tracking_products(self):
        # Create a products
        product1 = self.Product.create(
            {
                "name": "Test Product 11",
                "type": "product",
                "default_code": "TEST_PROD11",
                "tracking": "lot",
            }
        )
        product2 = self.Product.create(
            {
                "name": "Test Product 22",
                "type": "product",
                "default_code": "TEST_PROD22",
                "tracking": "serial",
            }
        )

        # Create a IN picking product 1
        incoming_picking1 = (
            self.StockPicking.with_context(default_company_id=self.company.id)
            .with_user(self.user_demo)
            .create(
                {
                    "location_dest_id": self.input_location.id,
                    "picking_type_id": self.in_type.id,
                }
            )
        )
        move_line1 = self.StockMoveLine.create(
            {
                "product_id": product1.id,
                "product_uom_id": self.uom_unit.id,
                "qty_done": 3.0,
                "picking_id": incoming_picking1.id,
                "lot_name": "LOT11",
            }
        )
        # Put in pack, in order to use this package for testing the move packages logic
        incoming_picking1.action_put_in_pack()
        incoming_picking1.action_confirm()
        incoming_picking1.button_validate()

        internal_picking1 = self.StockPicking.search(
            [("origin", "=", incoming_picking1.name)]
        )
        package_level1 = internal_picking1.package_level_ids
        package_level1.write({"is_done": True})
        internal_picking1.action_confirm()
        internal_picking1.button_validate()
        package1 = package_level1.package_id

        # Create a IN picking product 2
        incoming_picking2 = (
            self.StockPicking.with_context(default_company_id=self.company.id)
            .with_user(self.user_demo)
            .create(
                {
                    "location_dest_id": self.input_location.id,
                    "picking_type_id": self.in_type.id,
                }
            )
        )
        move_line2 = self.StockMoveLine.create(
            {
                "product_id": product2.id,
                "product_uom_id": self.uom_unit.id,
                "qty_done": 1.0,
                "picking_id": incoming_picking2.id,
                "lot_name": "SERIAL22",
            }
        )
        # Put in pack, in order to use this package for testing the move packages logic
        incoming_picking2.action_put_in_pack()
        incoming_picking2.action_confirm()
        incoming_picking2.button_validate()

        internal_picking2 = self.StockPicking.search(
            [("origin", "=", incoming_picking2.name)]
        )

        package_level2 = internal_picking2.package_level_ids
        package2 = package_level2.package_id

        # Move package2 to package1
        package_level2.package_dest_id = package1
        self.assertTrue(package_level2.is_done)

        # Validate the picking
        internal_picking2.action_confirm()
        internal_picking2.button_validate()

        # Test if only one quant is created per line
        quant1 = self.StockQuant.search(
            [
                ("lot_id", "=", move_line1.lot_id.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        quant2 = self.StockQuant.search(
            [
                ("lot_id", "=", move_line2.lot_id.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        self.assertEqual(len(quant1), 1)
        self.assertEqual(len(quant2), 1)

        # Test if all pickings are done
        self.assertEqual(incoming_picking1.state, "done")
        self.assertEqual(incoming_picking2.state, "done")
        self.assertEqual(internal_picking1.state, "done")
        self.assertEqual(internal_picking2.state, "done")

        # Test if the source package is empty
        self.assertEqual(len(package2.quant_ids), 0)

        # Test if the destination package contains the content from the source package
        self.assertEqual(len(package1.quant_ids), 2)
        self.assertIn(
            product1,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            product2,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )

        # Check the available product qty of product1 and product2 after the operations
        self.assertEqual(
            product1.qty_available, 3.0, "Total product quantity is not as expected."
        )
        self.assertEqual(
            product2.qty_available, 1.0, "Total product quantity is not as expected."
        )

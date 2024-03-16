# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase
from odoo.tests.common import Form


class TestStockQuantPackageFastMove(TransactionCase):
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
        group_tracking_lot = cls.env.ref("stock.group_tracking_lot")
        cls.user_demo.write(
            {
                "company_id": cls.company.id,
                "company_ids": [(4, cls.company.id)],
                "groups_id": [
                    (4, group_stock_multi_locations.id, 0),
                    (4, group_stock_adv_location.id, 0),
                    (4, group_tracking_lot.id, 0),
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
        cls.child_stock_location = cls.env["stock.location"].create(
            {
                "name": "Test Location",
                "location_id": cls.stock_location.id,
                "company_id": cls.company.id,
            }
        )
        cls.warehouse = cls.stock_location.warehouse_id
        cls.warehouse.write({"reception_steps": "two_steps"})
        cls.input_location = cls.warehouse.wh_input_stock_loc_id
        cls.in_type = cls.warehouse.in_type_id
        cls.in_type.write({"show_entire_packs": True})
        cls.int_type = cls.warehouse.int_type_id
        cls.int_type.write({"show_entire_packs": True})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.company.write({"package_move_picking_type_id": cls.int_type.id})
        cls.product1 = cls.Product.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "default_code": "TEST_PROD1",
                "tracking": "none",
            }
        )
        cls.product2 = cls.Product.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "default_code": "TEST_PROD2",
                "tracking": "none",
            }
        )
        cls.product3 = cls.Product.create(
            {
                "name": "Test Product 3",
                "type": "product",
                "default_code": "TEST_PROD3",
                "tracking": "lot",
            }
        )
        cls.product4 = cls.Product.create(
            {
                "name": "Test Product 4",
                "type": "product",
                "default_code": "TEST_PROD4",
                "tracking": "serial",
            }
        )
        # Create a IN picking with product 1, confirm it and move it in Stock location
        incoming_picking1 = (
            cls.StockPicking.with_context(default_company_id=cls.company.id)
            .with_user(cls.user_demo)
            .create(
                {
                    "location_dest_id": cls.input_location.id,
                    "picking_type_id": cls.in_type.id,
                }
            )
        )
        cls.StockMoveLine.create(
            {
                "product_id": cls.product1.id,
                "product_uom_id": cls.uom_unit.id,
                "qty_done": 3.0,
                "picking_id": incoming_picking1.id,
            }
        )
        incoming_picking1.action_put_in_pack()
        incoming_picking1.action_confirm()
        incoming_picking1.button_validate()

        internal_picking1 = cls.StockPicking.search(
            [("origin", "=", incoming_picking1.name)]
        )
        package_level1 = cls.PackageLevel.search(
            [("picking_id", "=", internal_picking1.id)]
        )
        package_level1.write({"is_done": True})
        internal_picking1.action_confirm()
        internal_picking1.button_validate()

        cls.package1 = package_level1.package_id

        # Create a IN picking with product 2 and product 3,
        # put in pack and leave it in Input location
        incoming_picking2 = (
            cls.StockPicking.with_context(default_company_id=cls.company.id)
            .with_user(cls.user_demo)
            .create(
                {
                    "location_dest_id": cls.input_location.id,
                    "picking_type_id": cls.in_type.id,
                }
            )
        )
        cls.StockMoveLine.create(
            [
                {
                    "product_id": cls.product2.id,
                    "product_uom_id": cls.uom_unit.id,
                    "qty_done": 2.0,
                    "picking_id": incoming_picking2.id,
                },
                {
                    "product_id": cls.product3.id,
                    "product_uom_id": cls.uom_unit.id,
                    "lot_name": "LOT/1",
                    "qty_done": 2.0,
                    "picking_id": incoming_picking2.id,
                },
            ]
        )
        incoming_picking2.action_put_in_pack()
        incoming_picking2.action_confirm()
        incoming_picking2.button_validate()

        internal_picking2 = cls.StockPicking.search(
            [("origin", "=", incoming_picking2.name)]
        )

        package_level2 = cls.PackageLevel.search(
            [("picking_id", "=", internal_picking2.id)]
        )
        cls.package2 = package_level2.package_id

        # Unreserve
        internal_picking2.do_unreserve()
        internal_picking2.unlink()

        # Create a IN picking with product 4, put in pack and leave it in Input location
        incoming_picking3 = (
            cls.StockPicking.with_context(default_company_id=cls.company.id)
            .with_user(cls.user_demo)
            .create(
                {
                    "location_dest_id": cls.input_location.id,
                    "picking_type_id": cls.in_type.id,
                }
            )
        )
        cls.StockMoveLine.create(
            [
                {
                    "product_id": cls.product4.id,
                    "product_uom_id": cls.uom_unit.id,
                    "qty_done": 1.0,
                    "lot_name": "SERIAL/1",
                    "picking_id": incoming_picking3.id,
                }
            ]
        )
        incoming_picking3.action_put_in_pack()
        incoming_picking3.action_confirm()
        incoming_picking3.button_validate()

        internal_picking3 = cls.StockPicking.search(
            [("origin", "=", incoming_picking3.name)]
        )

        package_level3 = cls.PackageLevel.search(
            [("picking_id", "=", internal_picking3.id)]
        )
        cls.package3 = package_level3.package_id
        # Unreserve
        internal_picking3.do_unreserve()
        internal_picking3.unlink()

    def test_stock_quant_package_fast_move(self):
        # Test if the optional field destination package is empty
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[self.package2.id, self.package3.id])
        ) as f1:
            f1.location_dest_id = self.int_type.default_location_dest_id
            f1.validate = True

        wizard = f1.save()
        wizard.action_move()

        # Check the available product qty of product1 product2
        # product3 and product 4 after the operations
        self.assertEqual(
            self.product1.qty_available,
            3.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product2.qty_available,
            2.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product3.qty_available,
            2.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product4.qty_available,
            1.0,
            "Total product quantity is not as expected.",
        )

        # Test if the destination package contains the content from the source package
        self.assertNotIn(
            self.product2,
            self.package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertNotIn(
            self.product3,
            self.package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertNotIn(
            self.product4,
            self.package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )

        # Check the location_id of the moved packages
        self.assertEqual(
            self.package2.location_id.id,
            self.int_type.default_location_dest_id.id,
            "Wrong location on the package.",
        )
        self.assertEqual(
            self.package3.location_id.id,
            self.int_type.default_location_dest_id.id,
            "Wrong location on the package.",
        )

    def test_stock_quant_package_fast_move_package(self):
        # Test if the optional field destination package is set
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[self.package2.id, self.package3.id])
        ) as f1:
            f1.location_dest_id = self.int_type.default_location_dest_id
            f1.package_dest_id = self.package1
            f1.validate = True

        wizard = f1.save()
        wizard.action_move()

        # Check the available product qty of product1 product2
        # product3 and product 4 after the operations
        self.assertEqual(
            self.product1.qty_available,
            3.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product2.qty_available,
            2.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product3.qty_available,
            2.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product4.qty_available,
            1.0,
            "Total product quantity is not as expected.",
        )

        # Test if the destination package contains the content from the source packages
        self.assertIn(
            self.product1,
            self.package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            self.product2,
            self.package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            self.product3,
            self.package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            self.product4,
            self.package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )

    def test_stock_quant_package_fast_move_package_error_same_location(self):
        # Check if the location is different from the current location
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[self.package2.id, self.package3.id])
        ) as f1:
            f1.location_dest_id = self.in_type.default_location_dest_id
            f1.validate = True

        wizard = f1.save()
        with self.assertRaises(UserError):
            wizard.action_move()

    def test_stock_quant_package_fast_move_package_error_package_same_location(self):
        # Check if the destination package belongs to the same location
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[self.package2.id])
        ) as f1:
            f1.location_dest_id = self.int_type.default_location_dest_id
            f1.package_dest_id = self.package3
            f1.validate = True

        wizard = f1.save()
        with self.assertRaises(UserError):
            wizard.action_move()

    def test_stock_quant_package_fast_move_packages_to_child_location(self):
        # Receive Package1 through all steps
        # Create a IN picking with product 1, put in pack, confirm it
        # and move it in Stock location
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
                "product_id": self.product1.id,
                "product_uom_id": self.uom_unit.id,
                "qty_done": 3.0,
                "picking_id": incoming_picking1.id,
            }
        )
        incoming_picking1.action_put_in_pack()
        incoming_picking1.action_confirm()
        incoming_picking1.button_validate()

        internal_picking1 = self.StockPicking.search(
            [("origin", "=", incoming_picking1.name)]
        )
        package_level1 = self.PackageLevel.search(
            [("picking_id", "=", internal_picking1.id)]
        )
        package_level1.write({"is_done": True})
        internal_picking1.action_confirm()
        internal_picking1.button_validate()

        package1 = package_level1.package_id

        # Receive Package2 through all steps
        # Create a IN picking with product 2 and product 3, put in pack, confirm it
        # and move it in Stock location
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
            [
                {
                    "product_id": self.product2.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty_done": 3.0,
                    "picking_id": incoming_picking2.id,
                },
                {
                    "product_id": self.product3.id,
                    "product_uom_id": self.uom_unit.id,
                    "lot_name": "LOT/11",
                    "qty_done": 2.0,
                    "picking_id": incoming_picking2.id,
                },
            ]
        )
        incoming_picking2.action_put_in_pack()
        incoming_picking2.action_confirm()
        incoming_picking2.button_validate()

        internal_picking2 = self.StockPicking.search(
            [("origin", "=", incoming_picking2.name)]
        )
        package_level2 = self.PackageLevel.search(
            [("picking_id", "=", internal_picking2.id)]
        )
        package_level2.write({"is_done": True})
        internal_picking2.action_confirm()
        internal_picking2.button_validate()

        package2 = package_level2.package_id

        # Move Package1 to child location
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[package1.id])
        ) as f1:
            f1.location_dest_id = self.child_stock_location
            f1.validate = True

        wizard = f1.save()
        wizard.action_move()

        # Move Package2 to the same location and select Package1 as a destination package
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[package2.id])
        ) as f2:
            f2.location_dest_id = self.child_stock_location
            f2.package_dest_id = package1
            f2.validate = True

        wizard = f2.save()
        wizard.action_move()

        # Check the available product qty of product1 product2 and
        # product3 after the operations
        self.assertEqual(
            self.product1.qty_available,
            6.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product2.qty_available,
            5.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product3.qty_available,
            4.0,
            "Total product quantity is not as expected.",
        )

        # Test if the destination package contains the content from the source packages
        self.assertIn(
            self.product1,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            self.product2,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            self.product3,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )

    def test_stock_quant_package_fast_move_packages_from_same_location(self):
        # Receive Package1 through all steps
        # Create a IN picking with product 1 and product 2, put in pack, confirm it
        # and move it in Stock location
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
            [
                {
                    "product_id": self.product1.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty_done": 3.0,
                    "picking_id": incoming_picking1.id,
                },
                {
                    "product_id": self.product2.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty_done": 3.0,
                    "picking_id": incoming_picking1.id,
                },
            ]
        )
        incoming_picking1.action_put_in_pack()
        incoming_picking1.action_confirm()
        incoming_picking1.button_validate()

        internal_picking1 = self.StockPicking.search(
            [("origin", "=", incoming_picking1.name)]
        )
        package_level1 = self.PackageLevel.search(
            [("picking_id", "=", internal_picking1.id)]
        )
        package_level1.write({"is_done": True})
        internal_picking1.action_confirm()
        internal_picking1.button_validate()

        package1 = package_level1.package_id

        # Receive Package2 through all steps
        # Create a IN picking with product 3, put in pack, confirm it
        # and move it in Stock location
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
                "product_id": self.product3.id,
                "product_uom_id": self.uom_unit.id,
                "lot_name": "LOT/11",
                "qty_done": 2.0,
                "picking_id": incoming_picking2.id,
            },
        )
        incoming_picking2.action_put_in_pack()
        incoming_picking2.action_confirm()
        incoming_picking2.button_validate()

        internal_picking2 = self.StockPicking.search(
            [("origin", "=", incoming_picking2.name)]
        )
        package_level2 = self.PackageLevel.search(
            [("picking_id", "=", internal_picking2.id)]
        )
        package_level2.write({"is_done": True})
        internal_picking2.action_confirm()
        internal_picking2.button_validate()

        package2 = package_level2.package_id

        # Move Package2 content to Package1
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[package2.id])
        ) as f1:
            f1.location_dest_id = self.stock_location
            f1.package_dest_id = package1
            f1.validate = True

        wizard = f1.save()
        wizard.action_move()

        # Check the available product qty of product1 product2 and
        # product3 after the operations
        self.assertEqual(
            self.product1.qty_available,
            6.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product2.qty_available,
            5.0,
            "Total product quantity is not as expected.",
        )
        self.assertEqual(
            self.product3.qty_available,
            4.0,
            "Total product quantity is not as expected.",
        )

        # Test if the destination package contains the content from the source packages
        self.assertIn(
            self.product1,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            self.product2,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )
        self.assertIn(
            self.product3,
            package1.quant_ids.mapped("product_id"),
            msg="Product not found in the destination package.",
        )

    def test_stock_quant_package_fast_move_no_picking_validation(self):
        # Test no picking validation
        with Form(
            self.env["stock.quant.package.fast.move.wizard"]
            .with_company(self.company.id)
            .with_context(active_ids=[self.package2.id, self.package3.id])
        ) as f1:
            f1.location_dest_id = self.int_type.default_location_dest_id

        wizard = f1.save()
        wizard.action_move()

        # Check the location_id; it should remain unchanged.
        self.assertNotEqual(
            self.package2.location_id.id,
            self.int_type.default_location_dest_id.id,
            "Wrong location on the package.",
        )
        self.assertNotEqual(
            self.package3.location_id.id,
            self.int_type.default_location_dest_id.id,
            "Wrong location on the package.",
        )
        # Check that the state of the created internal picking is set to 'assigned'.
        picking_ids = (
            self.env["stock.move.line"]
            .search([("result_package_id", "in", [self.package2.id, self.package3.id])])
            .picking_id
        )
        picking_id = picking_ids.filtered(
            lambda picking: picking.picking_type_code == "internal"
        )
        self.assertEqual(
            picking_id.state,
            "assigned",
            "Wrong picking state.",
        )

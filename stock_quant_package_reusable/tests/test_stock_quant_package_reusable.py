# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.stock.tests.test_packing import TestPackingCommon


@tagged("post_install", "-at_install")
class TestReusablePacking(TestPackingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Supplier Location
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        # Create valid reusable packages
        cls.reusable_pkg_in = cls.env["stock.quant.package"].create(
            {
                "name": "Reusable Box IN",
                "package_use": "reusable",
                "location_id": cls.stock_location.id,
            }
        )
        cls.reusable_pkg_out = cls.env["stock.quant.package"].create(
            {
                "name": "Reusable Box OUT",
                "package_use": "reusable",
                "location_id": cls.stock_location.id,
            }
        )
        # Create **invalid** disposable/reusable packages
        # Disposable package in internal stock.location
        cls.disposable_pkg = cls.env["stock.quant.package"].create(
            {
                "name": "Disposable Box",
                "package_use": "disposable",
                "location_id": cls.stock_location.id,
            }
        )
        # Reusable package in external stock.location
        cls.external_pkg = cls.env["stock.quant.package"].create(
            {
                "name": "External Box",
                "package_use": "reusable",
                "location_id": cls.customer_location.id,
            }
        )
        # Reusable Package in other stock.warehouse
        warehouse2 = cls.env["stock.warehouse"].create({"name": "WH2", "code": "WH2"})
        cls.wh2_pkg = cls.env["stock.quant.package"].create(
            {
                "name": "WH2 Box",
                "package_use": "reusable",
                "location_id": warehouse2.lot_stock_id.id,
            }
        )

        # Enable Reusable Pack on Picking Types
        cls.warehouse.in_type_id.use_reusable_pack = True
        cls.warehouse.out_type_id.use_reusable_pack = True

    def test_00_package_domain(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        wizard = self.env["select.reusable.package"].create(
            {
                "picking_id": picking.id,
                "package_id": self.reusable_pkg_out.id,
            }
        )
        expected_domain = [
            ("package_use", "=", "reusable"),
            ("location_id.usage", "=", "internal"),
            ("location_id", "child_of", wizard.warehouse_view_location_id.id),
        ]
        available_packages = self.env["stock.quant.package"].search(expected_domain)
        # Should contain our valid packages
        self.assertIn(self.reusable_pkg_in, available_packages)
        self.assertIn(self.reusable_pkg_out, available_packages)

        # Should NOT contain invalid packages
        self.assertNotIn(
            self.disposable_pkg,
            available_packages,
            "Disposable packages should be filtered out",
        )
        self.assertNotIn(
            self.external_pkg,
            available_packages,
            "Packages in external locations should be filtered out",
        )
        self.assertNotIn(
            self.wh2_pkg,
            available_packages,
            "Packages in other warehouses should be filtered out",
        )

    def test_01_receipt_flow(self):
        # Create Receipt
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )

        self.env["stock.move"].create(
            {
                "name": self.productA.name,
                "product_id": self.productA.id,
                "product_uom_qty": 10.0,
                "product_uom": self.productA.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )

        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.picked = True

        lines_to_pack = picking.move_line_ids
        action = picking.action_put_in_pack(move_lines_to_pack=lines_to_pack)

        self.assertIsInstance(action, dict, "Put in Pack should trigger wizard action")
        self.assertEqual(action.get("res_model"), "select.reusable.package")

        # Verify the lines were passed into the context for the wizard
        self.assertEqual(
            action["context"].get("move_lines_to_pack"),
            lines_to_pack,
            "The specific lines to pack must be passed to the wizard context",
        )

        # Select Reusable Box IN via Wizard
        Wizard = self.env["select.reusable.package"].with_context(**action["context"])
        wizard = Wizard.create(
            {
                "picking_id": picking.id,
                "package_id": self.reusable_pkg_in.id,
            }
        )
        self.assertEqual(
            wizard.env.context.get("move_lines_to_pack"),
            lines_to_pack,
            "The specific lines to pack must be present in the wizard context",
        )

        # Confirm Wizard - This triggers the second call to action_put_in_pack
        # The logic inside wizard.action_confirm() must retrieve 'move_lines_to_pack'
        # from context and pass it to picking.action_put_in_pack()
        wizard.action_confirm()

        move_line = picking.move_line_ids[0]
        self.assertEqual(
            move_line.result_package_id,
            self.reusable_pkg_in,
            "Receipt items should be packed into Reusable Box IN",
        )

        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def test_02_delivery_flow(self):
        # Setup Stock
        self.env["stock.quant"]._update_available_quantity(
            self.productB, self.stock_location, 5.0
        )

        # Create Delivery
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )

        self.env["stock.move"].create(
            {
                "name": self.productB.name,
                "product_id": self.productB.id,
                "product_uom_qty": 5.0,
                "product_uom": self.productB.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )

        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.picked = True

        lines_to_pack = picking.move_line_ids
        action = picking.action_put_in_pack(move_lines_to_pack=lines_to_pack)

        self.assertIsInstance(action, dict, "Put in Pack should trigger wizard action")
        self.assertEqual(action.get("res_model"), "select.reusable.package")

        # Verify the lines were passed into the context for the wizard
        self.assertEqual(
            action["context"].get("move_lines_to_pack"),
            lines_to_pack,
            "The specific lines to pack must be passed to the wizard context",
        )

        # Select Reusable Box OUT via Wizard
        Wizard = self.env["select.reusable.package"].with_context(**action["context"])
        wizard = Wizard.create(
            {
                "picking_id": picking.id,
                "package_id": self.reusable_pkg_out.id,
            }
        )
        self.assertEqual(
            wizard.env.context.get("move_lines_to_pack"),
            lines_to_pack,
            "The specific lines to pack must be present in the wizard context",
        )

        wizard.action_confirm()

        move_line = picking.move_line_ids[0]
        self.assertEqual(
            move_line.result_package_id,
            self.reusable_pkg_out,
            "Delivery items should be packed into Reusable Box OUT",
        )

        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def test_03_standard_receipt_flow(self):
        # Disable Feature
        self.warehouse.in_type_id.use_reusable_pack = False

        # Create Receipt
        picking_in = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Receipt Fallback",
                "product_id": self.productA.id,
                "product_uom_qty": 2.0,
                "product_uom": self.productA.uom_id.id,
                "picking_id": picking_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        picking_in.action_confirm()
        picking_in.action_assign()
        picking_in.move_ids.picked = True

        lines_to_pack = picking_in.move_line_ids

        res_in = picking_in.action_put_in_pack(move_lines_to_pack=lines_to_pack)

        # Should NOT be a wizard dict
        if isinstance(res_in, dict):
            self.assertNotEqual(res_in.get("res_model"), "select.reusable.package")

        # A new package was created
        move_line_in = picking_in.move_line_ids[0]
        self.assertTrue(
            move_line_in.result_package_id, "A standard package should be created"
        )
        self.assertNotEqual(
            move_line_in.result_package_id,
            self.reusable_pkg_in,
            "Should not reuse the existing box",
        )

    def test_04_standard_delivery_flow(self):
        # Disable Feature
        self.warehouse.out_type_id.use_reusable_pack = False

        # Setup Stock
        self.env["stock.quant"]._update_available_quantity(
            self.productA, self.stock_location, 5.0
        )

        # Create Delivery
        picking_out = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Delivery Fallback",
                "product_id": self.productA.id,
                "product_uom_qty": 5.0,
                "product_uom": self.productA.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking_out.action_confirm()
        picking_out.action_assign()
        picking_out.move_ids.picked = True

        lines_to_pack = picking_out.move_line_ids

        res_out = picking_out.action_put_in_pack(move_lines_to_pack=lines_to_pack)

        # Should NOT be a wizard dict
        if isinstance(res_out, dict):
            self.assertNotEqual(res_out.get("res_model"), "select.reusable.package")

        # A new package was created
        move_line_out = picking_out.move_line_ids[0]
        self.assertTrue(
            move_line_out.result_package_id, "A standard package should be created"
        )
        self.assertNotEqual(
            move_line_out.result_package_id,
            self.reusable_pkg_out,
            "Should not reuse the existing box",
        )

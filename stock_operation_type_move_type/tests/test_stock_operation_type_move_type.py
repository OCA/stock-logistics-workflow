# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockOperationTypeMoveType(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Get reference operation types
        cls.receipt_type = cls.env.ref("stock.picking_type_incoming")
        cls.delivery_type = cls.env.ref("stock.picking_type_outgoing")
        cls.internal_type = cls.env.ref("stock.picking_type_internal")

        # Create test operation types
        cls.test_receipt_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Receipt Type",
                "code": "incoming",
                "sequence_id": cls.env.ref("stock.seq_picking_internal").id,
                "default_move_type": "direct",
            }
        )

        cls.test_delivery_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Delivery Type",
                "code": "outgoing",
                "sequence_id": cls.env.ref("stock.seq_picking_internal").id,
                "default_move_type": "one",
            }
        )

        cls.test_internal_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Internal Type",
                "code": "internal",
                "sequence_id": cls.env.ref("stock.seq_picking_internal").id,
                "default_move_type": "direct",
            }
        )

        # Create test products
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "product",
            }
        )

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "product",
            }
        )

        # Create stock locations
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def test_default_move_type_field_exists(self):
        """Test that default_move_type field exists on stock.picking.type"""
        self.assertTrue(hasattr(self.test_receipt_type, "default_move_type"))
        self.assertEqual(self.test_receipt_type.default_move_type, "direct")
        self.assertEqual(self.test_delivery_type.default_move_type, "one")

    def test_default_move_type_selection_values(self):
        """Test that default_move_type has correct selection values"""
        selection_values = self.test_receipt_type._fields["default_move_type"].selection
        expected_values = [
            ("direct", "As soon as possible"),
            ("one", "When all products are ready"),
        ]
        self.assertEqual(selection_values, expected_values)

    def test_picking_creation_with_operation_type_default(self):
        """Test that picking creation uses operation type default move_type"""
        # Test with direct default
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.test_receipt_type.id,
                "partner_id": self.env.ref("base.res_partner_1").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.assertEqual(picking.move_type, "direct")

        # Test with one default
        picking2 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.test_delivery_type.id,
                "partner_id": self.env.ref("base.res_partner_1").id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.assertEqual(picking2.move_type, "one")

    def test_picking_creation_explicit_move_type_override(self):
        """Test that explicit move_type overrides operation type default"""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.test_receipt_type.id,  # Has 'direct' default
                "partner_id": self.env.ref("base.res_partner_1").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_type": "one",  # Explicit override
            }
        )
        self.assertEqual(picking.move_type, "one")

    def test_picking_creation_no_operation_type(self):
        """Test fallback when no operation type is specified"""
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        # Should not crash and should have default behavior
        self.assertTrue(picking.exists())

    def test_picking_creation_operation_type_no_default(self):
        """Test fallback when operation type has no default_move_type"""
        # Create operation type without default
        op_type_no_default = self.env["stock.picking.type"].create(
            {
                "name": "No Default Type",
                "code": "incoming",
                "sequence_id": self.env.ref("stock.seq_picking_internal").id,
                # default_move_type not set
            }
        )

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": op_type_no_default.id,
                "partner_id": self.env.ref("base.res_partner_1").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        # Should not crash and should have default behavior
        self.assertTrue(picking.exists())

    def test_field_visibility_in_form(self):
        """Test that default_move_type field is visible for relevant operation types"""
        # Check that field exists and is accessible
        self.assertTrue(self.test_receipt_type.fields_get(["default_move_type"]))

        # Field should be visible for incoming, outgoing, internal types
        for op_type in [
            self.test_receipt_type,
            self.test_delivery_type,
            self.test_internal_type,
        ]:
            field_info = op_type.fields_get(["default_move_type"])
            self.assertIn("default_move_type", field_info)

    def test_field_help_text(self):
        """Test that field has proper help text"""
        field_def = self.test_receipt_type._fields["default_move_type"]
        self.assertIn("Default shipping policy", field_def.help or "")

    def test_multiple_picking_creation(self):
        """Test create_multi method with multiple vals"""
        vals_list = [
            {
                "picking_type_id": self.test_receipt_type.id,
                "partner_id": self.env.ref("base.res_partner_1").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            },
            {
                "picking_type_id": self.test_delivery_type.id,
                "partner_id": self.env.ref("base.res_partner_2").id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            },
        ]

        pickings = self.env["stock.picking"].create(vals_list)
        self.assertEqual(len(pickings), 2)
        self.assertEqual(pickings[0].move_type, "direct")  # From receipt type
        self.assertEqual(pickings[1].move_type, "one")  # From delivery type

    def test_operation_type_codes(self):
        """Test that field works with different operation type codes"""
        codes_and_defaults = {
            "incoming": "direct",
            "outgoing": "one",
            "internal": "direct",
        }

        for code, expected_default in codes_and_defaults.items():
            op_type = self.env["stock.picking.type"].create(
                {
                    "name": f"Test {code} Type",
                    "code": code,
                    "sequence_id": self.env.ref("stock.seq_picking_internal").id,
                    "default_move_type": expected_default,
                }
            )

            picking = self.env["stock.picking"].create(
                {
                    "picking_type_id": op_type.id,
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.stock_location.id,
                }
            )

            self.assertEqual(picking.move_type, expected_default)

    def test_field_required_behavior(self):
        """Test field behavior when not set (should not be required)"""
        op_type_no_default = self.env["stock.picking.type"].create(
            {
                "name": "No Required Field Test",
                "code": "incoming",
                "sequence_id": self.env.ref("stock.seq_picking_internal").id,
                # default_move_type intentionally not set
            }
        )

        # Should be able to create without default_move_type
        self.assertTrue(op_type_no_default.exists())
        self.assertFalse(op_type_no_default.default_move_type)

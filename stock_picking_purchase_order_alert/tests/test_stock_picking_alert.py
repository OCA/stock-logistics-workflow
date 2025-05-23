from odoo import api
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestStockPickingAlert(SavepointCase):
    """Test cases for Stock Picking Purchase Order Alert functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = api.Environment(cls.cr, cls.uid, {})

        # Get required references
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.warehouse.in_type_id

        # Create vendor
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Test Vendor",
                "supplier_rank": 1,
            }
        )

        # Create test products with different UoMs
        cls.products = {
            "unit": cls.env["product.product"].create(
                {
                    "name": "Test Product (Unit)",
                    "type": "product",
                    "uom_id": cls.uom_unit.id,
                    "uom_po_id": cls.uom_unit.id,
                }
            ),
            "dozen": cls.env["product.product"].create(
                {
                    "name": "Test Product (Dozen)",
                    "type": "product",
                    "uom_id": cls.uom_unit.id,
                    "uom_po_id": cls.uom_dozen.id,
                }
            ),
            "weight": cls.env["product.product"].create(
                {
                    "name": "Test Product (KG)",
                    "type": "product",
                    "uom_id": cls.uom_kg.id,
                    "uom_po_id": cls.uom_kg.id,
                }
            ),
        }

        # Configure picking type
        cls._configure_picking_type()

        # Create and confirm purchase order
        cls.po = cls._create_purchase_order()
        cls.po.button_confirm()

    @classmethod
    def _configure_picking_type(cls):
        """Configure picking type with alert settings."""
        cls.picking_type_in.write(
            {
                "display_quantity_alert_percentage": True,
                "quantity_alert_percentage": 30.0,
            }
        )

    @classmethod
    def _create_purchase_order(cls):
        """Create a purchase order with multiple products and UoMs."""
        return cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.products["unit"].id,
                            "product_qty": 10.0,
                            "product_uom": cls.uom_unit.id,
                            "price_unit": 100.0,
                            "name": cls.products["unit"].name,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.products["dozen"].id,
                            "product_qty": 1.0,
                            "product_uom": cls.uom_dozen.id,
                            "price_unit": 1000.0,
                            "name": cls.products["dozen"].name,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.products["weight"].id,
                            "product_qty": 100.0,
                            "product_uom": cls.uom_kg.id,
                            "price_unit": 50.0,
                            "name": cls.products["weight"].name,
                        },
                    ),
                ],
            }
        )

    def _get_picking_move(self, picking, product):
        """Helper method to get move line for a product in picking."""
        return picking.move_ids_without_package.filtered(
            lambda m: m.product_id == product
        )

    def test_01_no_alert_within_threshold(self):
        """Test no alert when quantities are within threshold."""
        picking = self.po.picking_ids[0]
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty

        # No alert should be present
        picking._compute_has_quantity_alert()
        self.assertFalse(picking.has_quantity_alert)

    def test_02_alert_exceeding_threshold(self):
        """Test alert when quantities exceed threshold."""
        picking = self.po.picking_ids[0]
        move = self._get_picking_move(picking, self.products["unit"])
        move.quantity_done = move.product_uom_qty * 1.5  # 50% more

        # Alert should be present
        picking._compute_has_quantity_alert()
        self.assertTrue(picking.has_quantity_alert)

    def test_03_alert_mixed_quantities(self):
        """Test alert with mixed quantities (some over, some under threshold)."""
        picking = self.po.picking_ids[0]

        # Set one product over threshold
        move_unit = self._get_picking_move(picking, self.products["unit"])
        move_unit.quantity_done = move_unit.product_uom_qty * 1.4  # 40% more

        # Set another product within threshold
        move_dozen = self._get_picking_move(picking, self.products["dozen"])
        move_dozen.quantity_done = move_dozen.product_uom_qty * 1.1  # 10% more

        # Alert should be present due to unit product
        picking._compute_has_quantity_alert()
        self.assertTrue(picking.has_quantity_alert)
        self.assertIn("40.00%", picking.quantity_alert_message)
        self.assertIn(
            self.products["unit"].display_name, picking.quantity_alert_message
        )
        self.assertNotIn(
            self.products["dozen"].display_name, picking.quantity_alert_message
        )

    def test_04_alert_disabled(self):
        """Test no alert when feature is disabled."""
        # Disable alert feature
        self.picking_type_in.display_quantity_alert_percentage = False

        picking = self.po.picking_ids[0]
        move = self._get_picking_move(picking, self.products["unit"])
        move.quantity_done = move.product_uom_qty * 2  # 100% more

        # No alert should be present when feature is disabled
        picking._compute_has_quantity_alert()
        self.assertFalse(picking.has_quantity_alert)

    def test_05_alert_blocks_validation(self):
        """Test that alert blocks picking validation."""
        picking = self.po.picking_ids[0]
        move = self._get_picking_move(picking, self.products["unit"])
        move.quantity_done = move.product_uom_qty * 1.5  # 50% more

        # Attempt to validate picking should raise UserError
        with self.assertRaises(UserError):
            picking.button_validate()

    def test_06_alert_multiple_products(self):
        """Test alert with multiple products, one exceeding threshold."""
        picking = self.po.picking_ids[0]

        # Set quantities
        move_unit = self._get_picking_move(picking, self.products["unit"])
        move_dozen = self._get_picking_move(picking, self.products["dozen"])

        move_unit.quantity_done = move_unit.product_uom_qty * 1.4  # 40% over
        move_dozen.quantity_done = move_dozen.product_uom_qty * 1.1  # 10% over

        picking._compute_has_quantity_alert()
        self.assertTrue(picking.has_quantity_alert)
        self.assertIn("40.00%", picking.quantity_alert_message)
        self.assertIn(
            self.products["unit"].display_name, picking.quantity_alert_message
        )
        self.assertNotIn(
            self.products["dozen"].display_name, picking.quantity_alert_message
        )

    def test_07_alert_different_uom(self):
        """Test alert with product using different UoM."""
        picking = self.po.picking_ids[0]
        move = self._get_picking_move(picking, self.products["dozen"])
        move.quantity_done = move.product_uom_qty * 1.5  # 50% over

        picking._compute_has_quantity_alert()
        self.assertTrue(picking.has_quantity_alert)
        self.assertIn("50.00%", picking.quantity_alert_message)
        self.assertIn(
            self.products["dozen"].display_name, picking.quantity_alert_message
        )

    def test_08_button_validate_no_alert(self):
        """Test button_validate when no alert is present."""
        picking = self.po.picking_ids[0]
        move = self._get_picking_move(picking, self.products["unit"])
        move.quantity_done = move.product_uom_qty

        result = picking.button_validate()
        self.assertNotEqual(result["type"], "ir.actions.act_window")
        self.assertNotEqual(result["res_model"], "stock.picking.alert.wizard")

    def test_09_button_validate_multiple_pickings(self):
        """Test button_validate with multiple pickings."""
        # Create a second purchase order
        po2 = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.products["unit"].id,
                            "product_qty": 10.0,
                            "product_uom": self.uom_unit.id,
                            "price_unit": 100.0,
                            "name": self.products["unit"].name,
                        },
                    ),
                ],
            }
        )
        po2.button_confirm()
        picking2 = po2.picking_ids[0]

        # Set quantities for both pickings
        move1 = self._get_picking_move(self.po.picking_ids[0], self.products["unit"])
        move1.quantity_done = move1.product_uom_qty * 1.5  # 50% over

        move2 = self._get_picking_move(picking2, self.products["unit"])
        move2.quantity_done = move2.product_uom_qty * 1.1  # 10% over

        # First picking should raise alert
        with self.assertRaises(UserError):
            self.po.picking_ids[0].button_validate()

        # Second picking should validate normally
        result = picking2.button_validate()
        self.assertNotEqual(result["type"], "ir.actions.act_window")
        self.assertNotEqual(result["res_model"], "stock.picking.alert.wizard")
        self.picking_type_in.display_quantity_alert_percentage = False

        picking = self.po.picking_ids[0]
        move = self._get_picking_move(picking, self.products["unit"])
        move.quantity_done = move.product_uom_qty * 2  # 100% over
        move = self._get_picking_move(picking, self.product_unit)
        move.quantity_done = 20.0  # 100% over

        picking._compute_has_quantity_alert()
        self.assertFalse(picking.has_quantity_alert)
        self.assertFalse(picking.quantity_alert_message)

    def test_06_validate_with_alert(self):
        """Test validation blocked when quantity alert is active."""
        picking = self.po.picking_ids
        move = self._get_picking_move(picking, self.product_unit)
        move.quantity_done = 14.0  # 40% over

        with self.assertRaises(UserError):
            picking.button_validate()

        # Create purchase order
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 10.0,
                            "price_unit": 100.0,
                            "name": "Test PO Line",
                            "product_uom": self.uom_unit.id,
                            "date_planned": "2023-01-01",
                        },
                    )
                ],
            }
        )

        # Confirm purchase order to create picking
        self.po.button_confirm()
        self.picking = self.po.picking_ids[0]

    def test_quantity_alert_detection(self):
        """Test that verifies alert detection when
        received quantity exceeds threshold"""
        # Initially there should be no alert
        self.picking._compute_has_quantity_alert()
        self.assertFalse(self.picking.has_quantity_alert)

        # Set a quantity that exceeds the threshold (>30%)
        po_line = self.po.order_line[0]
        move = self.picking.move_ids_without_package.filtered(
            lambda m: m.purchase_line_id == po_line
        )

        # Configure received quantity that exceeds by more than 30%
        # 10 ordered units * 1.4 = 14 units (40% excess)
        move.quantity_done = 14.0

        # Recalculate and verify that the alert is detected
        self.picking._compute_has_quantity_alert()
        self.assertTrue(self.picking.has_quantity_alert)
        self.assertTrue(self.picking.quantity_alert_message)

        # Verify that a quantity within the threshold does not generate an alert
        # 10 ordered units * 1.2 = 12 units (20% excess, below the 30% threshold)
        move.quantity_done = 12.0
        self.picking._compute_has_quantity_alert()
        self.assertFalse(self.picking.has_quantity_alert)

    def test_button_validate_with_alert(self):
        """Test button_validate behavior when quantity alerts exist"""
        po_line = self.po.order_line[0]
        move = self.picking.move_ids_without_package.filtered(
            lambda m: m.purchase_line_id == po_line
        )

        # Case 1: Alert exists and bypass_alert not in context
        move.quantity_done = 14.0  # 40% excess
        self.picking._compute_has_quantity_alert()
        self.assertTrue(self.picking.has_quantity_alert)

        # Validate should open alert wizard
        result = self.picking.button_validate()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "stock.picking.alert.wizard")
        self.assertEqual(result["target"], "new")
        self.assertEqual(result["context"]["default_picking_id"], self.picking.id)

        # Case 2: Alert exists but bypass_alert is in context
        move.quantity_done = 14.0  # 40% excess
        self.picking._compute_has_quantity_alert()
        self.assertTrue(self.picking.has_quantity_alert)

        # Validate should proceed without wizard
        result = self.picking.with_context(bypass_alert=True).button_validate()
        self.assertNotEqual(result["type"], "ir.actions.act_window")
        self.assertNotEqual(result["res_model"], "stock.picking.alert.wizard")

        # Case 3: No alert exists
        move.quantity_done = 12.0  # 20% excess, below threshold
        self.picking._compute_has_quantity_alert()
        self.assertFalse(self.picking.has_quantity_alert)

        # Validate should proceed normally
        result = self.picking.button_validate()
        self.assertNotEqual(result["type"], "ir.actions.act_window")
        self.assertNotEqual(result["res_model"], "stock.picking.alert.wizard")

    def test_button_validate_multiple_pickings(self):
        """Test button_validate with multiple pickings"""
        # Create a second picking
        po2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 10.0,
                            "price_unit": 100.0,
                            "name": "Test PO Line",
                            "product_uom": self.uom_unit.id,
                            "date_planned": "2023-01-01",
                        },
                    )
                ],
            }
        )
        po2.button_confirm()
        picking2 = po2.picking_ids[0]

        # Set up alerts for both pickings
        for picking in [self.picking, picking2]:
            move = picking.move_ids_without_package.filtered(
                lambda m: m.purchase_line_id
                == picking.move_ids_without_package[0].purchase_line_id
            )
            if move:
                move.quantity_done = 14.0  # 40% excess
                picking._compute_has_quantity_alert()
                self.assertTrue(picking.has_quantity_alert)

        # Validate both pickings at once
        if self.picking and picking2:
            result = (self.picking | picking2).button_validate()
            self.assertEqual(result["type"], "ir.actions.act_window")
            self.assertEqual(result["res_model"], "stock.picking.alert.wizard")
            self.assertEqual(result["target"], "new")
            self.assertEqual(
                result["context"]["default_picking_id"], self.picking.id
            )  # First picking in recordset
        else:
            self.skipTest("Could not create both pickings for testing")

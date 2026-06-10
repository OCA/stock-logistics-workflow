from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, users


class TestStockPickingAlert(TransactionCase):
    """Test cases for Stock Picking Purchase Order Alert functionality."""

    def setUp(self):
        super().setUp()
        # self.env = api.Environment(self.cr, self.uid, {})

        # Get required references
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.uom_dozen = self.env.ref("uom.product_uom_dozen")
        self.uom_kg = self.env.ref("uom.product_uom_kgm")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.picking_type_in = self.env.ref("stock.picking_type_in")
        self.vendor = self.env.ref("base.res_partner_1")

        # Create test products with different UoMs
        self.products = {
            "unit": self.env["product.product"].create(
                {
                    "name": "Test Product (Unit)",
                    "type": "product",
                    "uom_id": self.uom_unit.id,
                    "uom_po_id": self.uom_unit.id,
                }
            ),
            "dozen": self.env["product.product"].create(
                {
                    "name": "Test Product (Dozen)",
                    "type": "product",
                    "uom_id": self.uom_unit.id,
                    "uom_po_id": self.uom_dozen.id,
                }
            ),
            "weight": self.env["product.product"].create(
                {
                    "name": "Test Product (KG)",
                    "type": "product",
                    "uom_id": self.uom_kg.id,
                    "uom_po_id": self.uom_kg.id,
                }
            ),
        }

        self.user_demo = self.env["res.users"].create(
            {
                "name": "Demo User",
                "login": "user_demo",
                "email": "user_demo@yourcompany.com",
            }
        )

        self.user_demo.groups_id |= self.env.ref("purchase.group_purchase_manager")
        self.user_demo.groups_id |= self.env.ref("stock.group_stock_manager")

        self.group_01 = self.env["res.groups"].create({"name": "Test Group"})

        # Configure picking type
        self._configure_picking_type()

        # Create and confirm purchase order
        self.po = self._create_purchase_order()
        self.po.button_confirm()

    def _configure_picking_type(self):
        """Configure picking type with alert settings."""
        self.picking_type_in.write(
            {
                "display_quantity_alert_percentage": True,
                "quantity_alert_percentage": 30.0,
            }
        )

    def _create_purchase_order(self):
        """Create a purchase order with multiple products and UoMs."""
        return self.env["purchase.order"].create(
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
                    (
                        0,
                        0,
                        {
                            "product_id": self.products["dozen"].id,
                            "product_qty": 1.0,
                            "product_uom": self.uom_dozen.id,
                            "price_unit": 1000.0,
                            "name": self.products["dozen"].name,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.products["weight"].id,
                            "product_qty": 100.0,
                            "product_uom": self.uom_kg.id,
                            "price_unit": 50.0,
                            "name": self.products["weight"].name,
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

    @users("user_demo")
    def test_00_group_validation(self):
        self.picking_type_in.write({"groups_ids": [(4, self.group_01.id)]})
        picking = self.po.picking_ids[0]

        self.assertNotIn(self.user_demo.id, self.group_01.mapped("users").ids)
        self.user_demo.groups_id = [(4, self.group_01.id)]
        self.assertIn(self.user_demo.id, self.group_01.mapped("users").ids)
        with self.assertRaises(UserError):
            picking.button_validate()

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
        self.assertFalse(picking.has_quantity_alert)

    def test_05_alert_blocks_validation(self):
        """Test that alert blocks picking validation."""
        picking = self.po.picking_ids[0]
        move = self._get_picking_move(picking, self.products["unit"])
        move.quantity_done = move.product_uom_qty * 1.5  # 50% more
        wiz_act = picking.button_validate()
        self.assertEqual(wiz_act["res_model"], "stock.picking.alert.wizard")
        alert_wiz = (
            self.env[wiz_act["res_model"]].with_context(wiz_act["context"]).create({})
        )
        alert_wiz.action_confirm()

    def test_06_alert_multiple_products(self):
        """Test alert with multiple products, one exceeding threshold."""
        picking = self.po.picking_ids[0]

        # Set quantities
        move_unit = self._get_picking_move(picking, self.products["unit"])
        move_dozen = self._get_picking_move(picking, self.products["dozen"])

        move_unit.quantity_done = move_unit.product_uom_qty * 1.4  # 40% over
        move_dozen.quantity_done = move_dozen.product_uom_qty * 1.1  # 10% over
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
        self.assertTrue(picking.has_quantity_alert)
        self.assertIn("50.00%", picking.quantity_alert_message)
        self.assertIn(
            self.products["dozen"].display_name, picking.quantity_alert_message
        )

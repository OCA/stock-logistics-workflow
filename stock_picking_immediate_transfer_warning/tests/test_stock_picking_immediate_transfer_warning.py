# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingImmediateTransferWarning(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        # Put stock in the warehouse
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 10.0
        )

    def _create_picking(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product.name,
                "picking_id": picking.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        return picking

    def test_wizard_shown_when_no_moves_picked(self):
        """When no moves are explicitly picked, the wizard should appear."""
        picking = self._create_picking()
        self.assertEqual(picking.state, "assigned")
        # No moves are picked
        self.assertFalse(any(m.picked for m in picking.move_ids))
        # Moves have reserved quantity
        self.assertTrue(any(m.quantity > 0 for m in picking.move_ids))
        result = picking.with_context(show_immediate_warning=True).button_validate()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("res_model"), "stock.immediate.transfer.warning")

    def test_no_wizard_when_moves_picked(self):
        """When moves are explicitly picked, the wizard should not appear."""
        picking = self._create_picking()
        # Explicitly mark moves as picked
        picking.move_ids.picked = True
        result = picking.with_context(show_immediate_warning=True).button_validate()
        # Should not return the immediate transfer wizard
        if isinstance(result, dict):
            self.assertNotEqual(
                result.get("res_model"), "stock.immediate.transfer.warning"
            )

    def test_wizard_process_validates_picking(self):
        """Clicking Process in the wizard should validate the picking."""
        picking = self._create_picking()
        result = picking.with_context(show_immediate_warning=True).button_validate()
        self.assertEqual(result.get("res_model"), "stock.immediate.transfer.warning")
        # Simulate the wizard process
        wizard = (
            self.env["stock.immediate.transfer.warning"]
            .with_context(**result.get("context", {}))
            .create({"pick_ids": [(4, picking.id)]})
        )
        wizard.process()
        self.assertEqual(picking.state, "done")

    def test_wizard_discard_keeps_picking_assigned(self):
        """Discarding the wizard should leave the picking unchanged."""
        picking = self._create_picking()
        result = picking.with_context(show_immediate_warning=True).button_validate()
        self.assertEqual(result.get("res_model"), "stock.immediate.transfer.warning")
        # User clicks Discard (does nothing, wizard is just closed)
        # The picking should remain assigned and moves not picked
        self.assertEqual(picking.state, "assigned")
        self.assertFalse(any(m.picked for m in picking.move_ids))

    def test_no_wizard_when_called_programmatically(self):
        """Programmatic calls without context should skip the wizard."""
        picking = self._create_picking()
        # Call without show_immediate_warning context — simulates programmatic call
        picking.button_validate()
        # Should validate directly without returning the wizard
        self.assertEqual(picking.state, "done")

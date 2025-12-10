# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2025 Open Source Integrators (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests import common


class TestStockLockLot(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create(
            {"name": "Test category", "lot_default_locked": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "categ_id": cls.category.id, "type": "product"}
        )
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.location = cls.warehouse.lot_stock_id

    def _get_lot_default_vals(self, name="Test lot", locked=False):
        return {
            "name": name,
            "product_id": self.product.id,
            "company_id": self.env.user.company_id.id,
            "locked": locked,
        }

    def _get_lot_quant(self, lot):
        """Get the quant for a specific lot."""
        return self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.location.id),
                ("lot_id", "=", lot.id),
            ]
        )

    def test_new_lot_unlocked(self):
        self.category.lot_default_locked = False
        lot = self.env["stock.lot"].create(self._get_lot_default_vals())
        self.assertFalse(lot.locked)

    def test_new_lot_locked(self):
        lot = self.env["stock.lot"].create(self._get_lot_default_vals())
        self.assertTrue(lot.locked)

    def test_lot_onchange_product(self):
        lot = self.env["stock.lot"].new(self._get_lot_default_vals())
        lot._onchange_product_id()
        self.assertTrue(lot.locked)

    def test_lock_permissions(self):
        self.env.user.groups_id -= self.env.ref("stock_lock_lot.group_lock_lot")
        # This should work correctly
        lot = self.env["stock.lot"].create(self._get_lot_default_vals())
        with self.assertRaises(exceptions.AccessError):
            lot.locked = False

    def test_locked_lot_excluded_from_reservation(self):
        """Test that locked lots are excluded from reservation."""
        # Create two lots - one locked, one unlocked
        locked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Locked Lot", locked=True)
        )
        unlocked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Unlocked Lot", locked=False)
        )

        # Create quants for both lots (_update_available_quantity returns tuple)
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 10, lot_id=locked_lot
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 10, lot_id=unlocked_lot
        )

        # Get the quant objects using helper function
        locked_quant = self._get_lot_quant(locked_lot)
        unlocked_quant = self._get_lot_quant(unlocked_lot)

        # Check initial availability - both should have 10 available
        self.assertEqual(locked_quant.available_quantity, 10.0)
        self.assertEqual(unlocked_quant.available_quantity, 10.0)

        # Try to create a stock move that would need to reserve inventory
        move = self.env["stock.move"].create(
            {
                "name": "Test move",
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.location.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        # Confirm the move to trigger reservation
        move._action_confirm()
        move._action_assign()

        # Refresh quants to get updated quantities
        locked_quant.invalidate_recordset()
        unlocked_quant.invalidate_recordset()

        # Only the unlocked lot should have been reserved
        self.assertEqual(
            locked_quant.reserved_quantity, 0.0, "Locked lot should not be reserved"
        )
        self.assertEqual(
            locked_quant.available_quantity,
            10.0,
            "Locked lot should still be available",
        )
        self.assertEqual(
            unlocked_quant.reserved_quantity, 5.0, "Unlocked lot should be reserved"
        )
        self.assertEqual(
            unlocked_quant.available_quantity,
            5.0,
            "Unlocked lot should have reduced availability",
        )

    def test_locked_lot_included_in_reservation_when_allowed(self):
        """Test that locked lots can be reserved when category allows it."""
        # Update category to allow reservation of locked lots
        self.category.lot_reserve_locked = False

        # Create two lots - one locked, one unlocked
        locked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Locked Lot", locked=True)
        )
        unlocked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Unlocked Lot", locked=False)
        )

        # Create quants for both lots (_update_available_quantity returns tuple)
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 10, lot_id=locked_lot
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 10, lot_id=unlocked_lot
        )

        # Get the quant objects using helper function
        locked_quant = self._get_lot_quant(locked_lot)
        unlocked_quant = self._get_lot_quant(unlocked_lot)

        # Check initial availability - both should have 10 available
        self.assertEqual(locked_quant.available_quantity, 10.0)
        self.assertEqual(unlocked_quant.available_quantity, 10.0)

        # Try to create a stock move that would need to reserve inventory
        move = self.env["stock.move"].create(
            {
                "name": "Test move",
                "product_id": self.product.id,
                "product_uom_qty": 15.0,  # Need more than unlocked lot has
                "product_uom": self.product.uom_id.id,
                "location_id": self.location.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        # Confirm the move to trigger reservation
        move._action_confirm()
        move._action_assign()

        # Refresh quants to get updated quantities
        locked_quant.invalidate_recordset()
        unlocked_quant.invalidate_recordset()

        # Both lots should have been reserved since category allows it
        self.assertEqual(
            locked_quant.reserved_quantity,
            5.0,
            "Locked lot should be reserved when allowed",
        )
        self.assertEqual(
            locked_quant.available_quantity,
            5.0,
            "Locked lot should have reduced availability",
        )
        self.assertEqual(
            unlocked_quant.reserved_quantity, 10.0, "Unlocked lot should be reserved"
        )
        self.assertEqual(
            unlocked_quant.available_quantity,
            0.0,
            "Unlocked lot should have no availability left",
        )

    def test_lot_level_reserve_locked_override(self):
        """Test that lot-level reserve_locked overrides category setting."""
        # Category does NOT allow reservation of locked lots
        self.category.lot_reserve_locked = False

        # Create a locked lot with lot-level override to allow reservation
        locked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Locked Lot", locked=True)
        )
        locked_lot.locked_reservation = False

        # Create an unlocked lot for comparison
        unlocked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Unlocked Lot", locked=False)
        )

        # Create quants for both lots
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 10, lot_id=locked_lot
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 10, lot_id=unlocked_lot
        )

        # Get the quant objects using helper function
        locked_quant = self._get_lot_quant(locked_lot)
        unlocked_quant = self._get_lot_quant(unlocked_lot)

        # Try to create a stock move that would need to reserve inventory
        move = self.env["stock.move"].create(
            {
                "name": "Test move",
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.location.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        # Confirm the move to trigger reservation
        move._action_confirm()
        move._action_assign()

        # Refresh quants to get updated quantities
        locked_quant.invalidate_recordset()
        unlocked_quant.invalidate_recordset()

        # The locked lot should be reserved due to lot-level override
        self.assertEqual(
            locked_quant.reserved_quantity,
            5.0,
            "Locked lot should be reserved with lot-level override",
        )
        self.assertEqual(
            locked_quant.available_quantity,
            5.0,
            "Locked lot should have reduced availability",
        )

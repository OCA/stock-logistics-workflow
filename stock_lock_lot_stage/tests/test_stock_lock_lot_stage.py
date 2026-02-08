# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests import common


class TestStockLotLockStage(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage_pending = cls.env.ref("stock_lock_lot_stage.lot_stage_pending")
        cls.stage_testing = cls.env.ref("stock_lock_lot_stage.lot_stage_testing")
        cls.stage_partial = cls.env.ref(
            "stock_lock_lot_stage.lot_stage_partially_approved"
        )
        cls.stage_approved = cls.env.ref("stock_lock_lot_stage.lot_stage_approved")
        cls.stage_rejected = cls.env.ref("stock_lock_lot_stage.lot_stage_rejected")

        cls.category = cls.env["product.category"].create(
            {"name": "Test category", "lot_default_locked": False}
        )
        cls.category_locked = cls.env["product.category"].create(
            {"name": "Test category locked", "lot_default_locked": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "categ_id": cls.category.id, "type": "product"}
        )
        cls.product_locked = cls.env["product.product"].create(
            {
                "name": "Test product locked",
                "categ_id": cls.category_locked.id,
                "type": "product",
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.stock_location = cls.warehouse.lot_stock_id

        cls.lock_group = cls.env.ref("stock_lock_lot.group_lock_lot")
        cls.env.user.groups_id |= cls.lock_group

    def _create_lot(self, product=None, name="Test Lot"):
        return self.env["stock.lot"].create(
            {
                "name": name,
                "product_id": (product or self.product).id,
                "company_id": self.env.user.company_id.id,
            }
        )

    def _add_quant(self, lot, qty, location=None):
        self.env["stock.quant"]._update_available_quantity(
            lot.product_id,
            location or self.stock_location,
            qty,
            lot_id=lot,
        )

    def test_stage_change_updates_locked(self):
        """Changing stage updates the locked flag."""
        lot = self._create_lot()
        self.assertEqual(lot.stage_id, self.stage_approved)
        self.assertFalse(lot.locked)

        lot.stage_id = self.stage_rejected
        self.assertTrue(lot.locked)

        lot.stage_id = self.stage_approved
        self.assertFalse(lot.locked)

    def test_new_lot_unlocked_product_gets_approved(self):
        """New lot for unlocked product starts as Approved."""
        lot = self._create_lot(self.product)
        self.assertEqual(lot.stage_id, self.stage_approved)
        self.assertFalse(lot.locked)

    def test_new_lot_locked_product_gets_pending(self):
        """New lot for locked product starts as Pending."""
        lot = self._create_lot(self.product_locked, "Locked Lot")
        self.assertEqual(lot.stage_id, self.stage_pending)
        self.assertTrue(lot.locked)

    def test_stage_change_permission(self):
        """Non-group user cannot change stage."""
        lot = self._create_lot()
        self.env.user.groups_id -= self.lock_group
        with self.assertRaises(exceptions.AccessError):
            lot.stage_id = self.stage_rejected

    def test_partial_approved_qty_permission(self):
        """Non-group user cannot change partial approved qty."""
        lot = self._create_lot()
        self.env.user.groups_id -= self.lock_group
        with self.assertRaises(exceptions.AccessError):
            lot.partial_approved_qty = 5.0

    def test_partial_approved_qty_blocks_move_to_restricted(self):
        """Cannot move to restricted location when exceeds partial approved qty."""
        lot = self._create_lot()
        lot.partial_approved_qty = 50.0

        # Create a restricted location (doesn't allow locked lots)
        restricted_location = self.env["stock.location"].create(
            {
                "name": "Restricted Location",
                "usage": "internal",
                "location_id": self.stock_location.location_id.id,
                "allow_locked": False,
            }
        )

        # Try to add quantity exceeding partial approved amount
        with self.assertRaises(exceptions.ValidationError) as cm:
            self.env["stock.quant"]._update_available_quantity(
                lot.product_id, restricted_location, 60.0, lot_id=lot
            )

        self.assertIn("exceeds the partial approved quantity", str(cm.exception))

    def test_partial_approved_qty_allows_move_to_restricted(self):
        """Can move to restricted location when within partial approved qty."""
        lot = self._create_lot()
        lot.partial_approved_qty = 50.0

        # Create a restricted location (doesn't allow locked lots)
        restricted_location = self.env["stock.location"].create(
            {
                "name": "Restricted Location",
                "usage": "internal",
                "location_id": self.stock_location.location_id.id,
                "allow_locked": False,
            }
        )

        # Add quantity within partial approved amount
        self.env["stock.quant"]._update_available_quantity(
            lot.product_id, restricted_location, 30.0, lot_id=lot
        )

        lot.invalidate_recordset()
        self.assertEqual(lot.usable_location_qty, 30.0)
        self.assertLessEqual(lot.usable_location_qty, lot.partial_approved_qty)

    def test_partial_approved_qty_ignores_allowed_locked_locations(self):
        """Quantities in locations allowing locked lots don't count towards
        restriction."""
        lot = self._create_lot()
        lot.partial_approved_qty = 50.0

        # Create a location that allows locked lots
        allowed_location = self.env["stock.location"].create(
            {
                "name": "Allowed Location",
                "usage": "internal",
                "location_id": self.stock_location.location_id.id,
                "allow_locked": True,
            }
        )

        # Add quantity exceeding partial approved amount to allowed location
        self.env["stock.quant"]._update_available_quantity(
            lot.product_id, allowed_location, 60.0, lot_id=lot
        )

        lot.invalidate_recordset()
        self.assertEqual(lot.usable_location_qty, 0.0)
        # Should not raise validation error

    def test_post_init_hook_sets_stages(self):
        """Verify lots have correct stages after hook (already ran at install)."""
        lot_unlocked = self._create_lot(name="Hook Unlocked")
        self.assertEqual(lot_unlocked.stage_id, self.stage_approved)

        lot_locked = self._create_lot(self.product_locked, "Hook Locked")
        self.assertEqual(lot_locked.stage_id, self.stage_pending)

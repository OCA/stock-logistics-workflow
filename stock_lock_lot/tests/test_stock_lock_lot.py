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
            {
                "name": "Test product",
                "categ_id": cls.category.id,
                "type": "product",
                "tracking": "lot",
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.location = cls.warehouse.lot_stock_id

        cls.lock_group = cls.env.ref("stock_lock_lot.group_lock_lot")
        cls.env.user.groups_id |= cls.lock_group

    def _get_lot_default_vals(self, name="Test lot"):
        return {
            "name": name,
            "product_id": self.product.id,
            "company_id": self.env.user.company_id.id,
        }

    def _get_lot_quant(self, lot):
        """Get the quant for a specific lot."""
        return self.env["stock.quant"].search(
            [
                ("product_id", "=", lot.product_id.id),
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
        self.env.user.groups_id -= self.lock_group
        # This should work correctly
        lot = self.env["stock.lot"].create(self._get_lot_default_vals())
        with self.assertRaises(exceptions.AccessError):
            lot.locked = False

    def test_locked_lot_excluded_from_reservation(self):
        """A locked lot is never reserved; its stock remains available."""
        # Create two lots - one locked, one unlocked. New lots are locked
        # automatically from the product category, so the second lot is
        # unlocked explicitly before any quantity exists.
        locked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Locked Lot")
        )
        unlocked_lot = self.env["stock.lot"].create(
            self._get_lot_default_vals(name="Unlocked Lot")
        )
        unlocked_lot.locked = False
        self.assertTrue(locked_lot.locked)
        self.assertFalse(unlocked_lot.locked)

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

        # The move must have reserved the unlocked lot
        self.assertEqual(move.move_line_ids.lot_id, unlocked_lot)

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

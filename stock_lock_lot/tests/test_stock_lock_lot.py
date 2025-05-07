# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions

from odoo.addons.base.tests.common import BaseCommon


class TestStockLockLot(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["product.category"].create(
            {"name": "Test category", "lot_default_locked": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "categ_id": cls.category.id, "is_storable": True}
        )

    def _get_lot_default_vals(self):
        return {
            "name": "Test lot",
            "product_id": self.product.id,
            "company_id": self.env.user.company_id.id,
        }

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

    def test_change_product_of_lot(self):
        lot = self.env["stock.lot"].create(self._get_lot_default_vals())
        new_category = self.env["product.category"].create(
            {"name": "New category", "lot_default_locked": False}
        )
        new_product = self.env["product.product"].create(
            {"name": "New product", "categ_id": new_category.id}
        )
        lot.write({"product_id": new_product.id})
        self.assertFalse(lot.locked)

    def test_block_unblock_with_reserved_quantities(self):
        lot = self.env["stock.lot"].create(self._get_lot_default_vals())
        location = self.env["stock.location"].create({"name": "Test location"})
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": location.id,
                "lot_id": lot.id,
                "quantity": 10.0,
                "reserved_quantity": 5.0,
            }
        )
        with self.assertRaises(exceptions.ValidationError):
            lot.locked = False

    def test_track_subtype(self):
        lot = self.env["stock.lot"].create(self._get_lot_default_vals())
        self.assertTrue(lot.locked)
        init_values = {"locked": False}
        subtype = lot._track_subtype(init_values)
        self.assertEqual(subtype, self.env.ref("stock_lock_lot.mt_lock_lot"))

        lot.write({"locked": False})
        self.assertFalse(lot.locked)
        init_values = {"locked": True}
        subtype = lot._track_subtype(init_values)
        self.assertEqual(subtype, self.env.ref("stock_lock_lot.mt_unlock_lot"))

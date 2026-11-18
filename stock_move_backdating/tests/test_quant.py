# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import TestCommon


@tagged("post_install", "-at_install")
class TestQuant(TestCommon):
    def _get_quant(self, product):
        return self.env["stock.quant"].search(
            [
                ("product_id", "=", product.id),
                ("location_id", "=", self.stock_location.id),
            ],
            limit=1,
        )

    def test_quant_inventory_fields_write_includes_date_backdating(self):
        """date_backdating is part of the quant inventory writable fields."""
        fields_write = self.env["stock.quant"]._get_inventory_fields_write()
        self.assertIn("date_backdating", fields_write)

    def test_quant_onchange_future_date_raises(self):
        """Setting a future date_backdating on a quant raises UserError."""
        future_date = self._get_datetime_backdating(-1)
        quant = self._get_quant(self.products[0])
        quant.date_backdating = future_date
        with self.assertRaises(UserError):
            quant.onchange_date_backdating()

    def test_quant_apply_inventory_backdating(self):
        """_apply_inventory propagates date_backdating to the generated move."""
        product = self.products[0]
        date_backdating = self._get_datetime_backdating(2)
        quant = self._get_quant(product)
        # Increase the quantity so _apply_inventory creates a move
        quant.with_context(inventory_mode=True).write(
            {
                "inventory_quantity": quant.quantity + 1,
                "date_backdating": date_backdating,
            }
        )
        quant._apply_inventory()
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", product.id),
                ("state", "=", "done"),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(move)
        self.assertEqual(move.move_line_ids[:1].date_backdating, date_backdating)
        # date_backdating is reset on the quant after applying
        self.assertFalse(quant.date_backdating)

    def test_quant_apply_inventory_without_backdating(self):
        """_apply_inventory works normally when no date_backdating is set."""
        product = self.products[1]
        quant = self._get_quant(product)
        quant.with_context(inventory_mode=True).write(
            {"inventory_quantity": quant.quantity + 1}
        )
        # Should not raise and date_backdating stays empty
        quant._apply_inventory()
        self.assertFalse(quant.date_backdating)

    def test_update_available_quantity_with_context(self):
        """_update_available_quantity uses date_backdating from context as in_date."""
        product = self.products[0]
        date_backdating = self._get_datetime_backdating(3)
        self.env["stock.quant"].with_context(
            date_backdating=date_backdating
        )._update_available_quantity(
            product,
            self.stock_location,
            1,
            lot_id=None,
            package_id=None,
            owner_id=None,
            in_date=None,
        )
        quants = self.env["stock.quant"]._gather(product, self.stock_location)
        self.assertTrue(any(q.in_date == date_backdating for q in quants))

    def test_update_available_quantity_keeps_min_in_date(self):
        """When both context date and in_date are passed, the earliest wins."""
        product = self.products[1]
        date_backdating = self._get_datetime_backdating(2)
        in_date = self._get_datetime_backdating(5)
        self.env["stock.quant"].with_context(
            date_backdating=date_backdating
        )._update_available_quantity(
            product,
            self.stock_location,
            1,
            lot_id=None,
            package_id=None,
            owner_id=None,
            in_date=in_date,
        )
        quants = self.env["stock.quant"]._gather(product, self.stock_location)
        self.assertTrue(any(q.in_date == in_date for q in quants))

    def test_quant_action_apply_inventory_passes_date(self):
        """Regression: applying an inventory adjustment via the UI action.

        Odoo 19's ``action_apply_inventory`` forwards a ``date`` argument to
        ``_apply_inventory`` (``self._apply_inventory(date)``). This override
        must accept and forward it -- otherwise applying *any* inventory
        adjustment raises ``TypeError: _apply_inventory() takes 1 positional
        argument but 2 were given``. This test drives the full UI action so the
        regression cannot reappear.
        """
        product = self.products[1]
        quant = self._get_quant(product)
        quant.with_context(inventory_mode=True).write(
            {"inventory_quantity": quant.quantity + 1}
        )
        # Drives stock.quant.action_apply_inventory -> _apply_inventory(date).
        quant.action_apply_inventory()
        move = self.env["stock.move"].search(
            [("product_id", "=", product.id), ("state", "=", "done")],
            order="id desc",
            limit=1,
        )
        self.assertTrue(move, "Inventory adjustment should create a done move")

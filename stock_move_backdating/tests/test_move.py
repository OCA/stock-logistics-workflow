# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from .common import TestCommon


@tagged("post_install", "-at_install")
class TestMove(TestCommon):
    def test_get_price_unit_no_context(self):
        """_get_price_unit returns the parent value when there's no backdating."""
        move = self.picking.move_ids[:1]
        # No date_backdating in context: returns whatever super returns
        self.assertIsNotNone(move._get_price_unit())

    def test_get_price_unit_no_purchase_line(self):
        """_get_price_unit returns the parent value when there's no purchase
        line, even with a date_backdating context set."""
        date_backdating = self._get_datetime_backdating(1)
        move = self.picking.move_ids[:1].with_context(date_backdating=date_backdating)
        # The purchase branch is skipped because purchase_line_id is not set,
        # so we just return super's result.
        self.assertIsNotNone(move._get_price_unit())

    def test_action_done_without_backdating(self):
        """Validating a picking with no date_backdating uses today as the
        date and exercises the else branch of _action_done."""
        for stock_move in self.picking.move_ids:
            stock_move.quantity = stock_move.product_uom_qty
        self.picking.button_validate()
        self.assertEqual(self.picking.state, "done")
        # No date_backdating set anywhere on the picking
        self.assertFalse(self.picking.date_backdating)

    def test_get_price_unit_purchase_same_currency(self):
        """Same-currency purchase: _convert is skipped and the override returns
        the PO price as a plain float (never a dict)."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase module not installed")
        partner = self.env["res.partner"].create({"name": "Test Vendor"})
        product = self.products[0]
        po = self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_qty": 1,
                            "product_uom_id": product.uom_id.id,
                            "price_unit": 50,
                            "name": product.name,
                            "date_planned": self._get_datetime_backdating(0),
                        },
                    ),
                ],
            }
        )
        po.button_confirm()
        in_move = po.picking_ids.move_ids[:1]
        date_backdating = self._get_datetime_backdating(1)
        result = in_move.with_context(date_backdating=date_backdating)._get_price_unit()
        # Same currency: no conversion, the PO price is returned as a float.
        self.assertIsInstance(result, float)
        self.assertEqual(result, 50)

    def test_get_price_unit_purchase_backdating(self):
        """When a purchase line exists with a foreign currency, _get_price_unit
        returns the price_unit converted at the backdated date."""
        if "purchase.order" not in self.env:
            self.skipTest("purchase module not installed")
        company = self.env.company
        other_currency = (
            self.env["res.currency"]
            .with_context(active_test=False)
            .search(
                [("id", "!=", company.currency_id.id)],
                limit=1,
            )
        )
        if not other_currency:
            self.skipTest("no alternative currency available")
        other_currency.active = True
        partner = self.env["res.partner"].create({"name": "Test Vendor"})
        product = self.products[0]
        po = self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "currency_id": other_currency.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_qty": 1,
                            "product_uom_id": product.uom_id.id,
                            "price_unit": 100,
                            "name": product.name,
                            "date_planned": self._get_datetime_backdating(0),
                        },
                    ),
                ],
            }
        )
        po.button_confirm()
        in_move = po.picking_ids.move_ids[:1]
        date_backdating = self._get_datetime_backdating(2)
        result = in_move.with_context(date_backdating=date_backdating)._get_price_unit()
        # The override returns the price converted to company currency at the
        # backdated date, as a float (never a dict).
        self.assertIsInstance(result, float)
        # Regression guard: a dict return here crashed real flows. Validating a
        # backdated delivery runs stock_account's ``_update_standard_price``,
        # which does ``standard_price = float(move._get_price_unit())`` for the
        # last incoming move, and ``_get_in_svl_vals`` does ``abs(...)`` on it.
        # A dict raised "TypeError: float() argument must be ... not 'dict'".
        # Exercise the exact operations that broke so this can never regress.
        self.assertEqual(float(result), result)
        self.assertGreaterEqual(abs(result), 0)

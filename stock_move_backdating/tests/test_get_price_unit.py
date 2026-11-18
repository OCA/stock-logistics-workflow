# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from .common import TestCommon


@tagged("post_install", "-at_install")
class TestGetPriceUnit(TestCommon):
    """Regression tests for ``stock.move._get_price_unit``.

    In Odoo 19 ``_get_price_unit`` is called on **multi-move recordsets**
    (e.g. ``sale_stock_margin._compute_purchase_price`` ->
    ``_get_price_unit_delivery`` -> ``regular_moves._get_price_unit()``).

    The backdating override used to ``self.ensure_one()`` and to return a
    ``{lot: price}`` dict, which crashed the 2nd transfer of a two-step
    delivery with ``ValueError: Expected singleton: stock.move(...)`` (and
    a ``TypeError`` in any caller doing arithmetic on the result).
    """

    def test_get_price_unit_multi_move_with_backdating(self):
        """A multi-move recordset must not raise and must return a number."""
        moves = self.picking.move_ids
        self.assertGreater(
            len(moves), 1, "Test fixture must provide a multi-move recordset"
        )
        date_backdating = self._get_datetime_backdating(5)
        # Must not raise "Expected singleton" ...
        price_unit = moves.with_context(
            date_backdating=date_backdating
        )._get_price_unit()
        # ... and must return a scalar, never a {lot: price} dict.
        self.assertNotIsInstance(price_unit, dict)
        self.assertIsInstance(price_unit, (int, float))

    def test_get_price_unit_single_move_with_backdating(self):
        """A single (non purchase-linked) move falls through to super()."""
        move = self.picking.move_ids[:1]
        date_backdating = self._get_datetime_backdating(5)
        price_unit = move.with_context(
            date_backdating=date_backdating
        )._get_price_unit()
        self.assertNotIsInstance(price_unit, dict)
        self.assertIsInstance(price_unit, (int, float))

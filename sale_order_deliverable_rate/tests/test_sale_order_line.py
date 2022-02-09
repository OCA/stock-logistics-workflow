# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import first
from odoo.tests.common import SavepointCase

from ..tests.common import TestCommonSale


class TestSaleOrderDeliverableRate(TestCommonSale, SavepointCase):
    def test_no_more_to_ship(self):
        """
        Ensure that qty_to_ship is to 0 when qty_delivered == product_uom_qty
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 10)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 10}
        )

        self.assertEqual(first(self.so_one_line.order_line).qty_to_ship, 0)

    def test_everything_to_ship(self):
        """
        Ensure that qty_to_ship is equal to product_uom_qty
        when qty_delivered is equal to 0
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 10)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 0}
        )

        self.assertEqual(
            first(self.so_one_line.order_line).qty_to_ship,
            first(self.so_one_line.order_line).product_uom_qty,
        )

    def test_qty_to_ship(self):
        """
        Ensure that qty_to_ship is equal to product_uom_qty - qty_delivered
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 10)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 5}
        )

        self.assertEqual(
            first(self.so_one_line.order_line).qty_to_ship,
            first(self.so_one_line.order_line).product_uom_qty
            - first(self.so_one_line.order_line).qty_to_ship,
        )

    def test_has_delivered_more(self):
        """
        Ensure that qty_to_ship is less than 0 when a product
        is over delivered (qty_delivered is greater than product_uom_qty)
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 10)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 11}
        )

        self.assertLess(first(self.so_one_line.order_line).qty_to_ship, 0)

    def test_totally_deliverable(self):
        """
        Ensure that deliverable_rate is to 100%
        when product has qty_available to satisfy product_uom_qty
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 10)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 0}
        )

        self.assertEqual(first(self.so_one_line.order_line).deliverable_rate, 100)

    def test_partially_deliverable(self):
        """
        Ensure that deliverable_rate is to 100%
        when product has qty_available to satisfy product_uom_qty
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 5)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 0}
        )

        self.assertEqual(first(self.so_one_line.order_line).deliverable_rate, 50)

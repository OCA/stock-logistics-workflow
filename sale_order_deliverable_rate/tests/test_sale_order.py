# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import first
from odoo.tests.common import SavepointCase

from ..tests.common import TestCommonSale


class TestSaleOrderDeliverableRate(TestCommonSale, SavepointCase):
    def test_totally_deliverable(self):
        """
        Ensure that deliverable_rate of an order is to 100%
        when it contains one order_line with a product who has enough stock
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 10)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 0}
        )

        self.assertEqual(self.so_one_line.deliverable_rate, 100)

    def test_partially_deliverable(self):
        """
        Ensure that deliverable_rate of an order is to 80%
        when it contains one order_line with a product who has
        stock to satisfy  order to 80%
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 8)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 0}
        )

        self.assertEqual(self.so_one_line.deliverable_rate, 80)

    def test_empty_order(self):
        """
        Ensure that deliverable_rate of an empty order is to 100%
        empty stand for an order with no order_lines
        :return:
        """

        self.assertEqual(self.so_empty.deliverable_rate, 0)

    def test_all_order_line_delivered(self):
        """
        Ensure that deliverable_rate of an order
        with all order_line delivered is to 0%
        :return:
        """
        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 10}
        )

        self.assertEqual(self.so_one_line.deliverable_rate, 0)

    def test_order_line_over_delivered(self):
        """
        Ensure that deliverable_rate of an order
        with order_line who has more qty_delivered
        than product_uom_qty is to 0%
        (has there is no more to deliver)
        :return:
        """
        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 11}
        )

        self.assertEqual(self.so_one_line.deliverable_rate, 0)

    def test_all_product_no_stock(self):
        """
        Ensure that deliverable_rate of an order is to 0%
        when all order_line has a product that has no stock
        :return:
        """
        for product in self.array_products:
            self._update_stock(product["product"], 0)

        self.assertEqual(self.so_three_line.deliverable_rate, 0)

    def test_search_deliverable_rate(self):
        """
        Ensure that the filter on deliverable_rate is finding order.
        To do so, we first create an order with a deliverable rate above
        80% then we search for order having a deliverable rate above 80%.
        it should be in the orders found. We change the deliverable and
        check if the order is not found anymore.
        :return:
        """
        self._update_stock(self.array_products[0]["product"], 9)

        first(self.so_one_line.order_line).write(
            {"product_uom_qty": 10, "qty_delivered": 0}
        )

        self.assertEqual(self.so_one_line.deliverable_rate, 90)

        orders = self.env["sale.order"].search([("deliverable_rate", ">=", 80)])

        self.assertTrue(orders)
        self.assertIn(self.so_one_line, orders)

        for order in orders:
            self.assertGreaterEqual(order.deliverable_rate, 80)

        # change the deliverable rate value by changing stock available
        self._update_stock(self.array_products[0]["product"], 7)

        self.assertEqual(self.so_one_line.deliverable_rate, 70)

        orders = self.env["sale.order"].search([("deliverable_rate", ">=", 80)])
        # check if the order is gone
        self.assertNotIn(self.so_one_line, orders)

    def test_order_line_service(self):
        """
        Ensure that order line with service product
        don't impact the deliverable rate.
        """
        self._update_stock(self.array_products[0]["product"], 10)

        self.assertEqual(self.so_with_service_line.deliverable_rate, 100)

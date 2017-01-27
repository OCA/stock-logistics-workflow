# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestDeliveryCarrier(TransactionCase):

    def setUp(self):
        super(TestDeliveryCarrier, self).setUp()

        self.test_model = self.env['delivery.carrier']

        test_order_1 = self.env.ref('sale_delivery_rate.demo_order_1')
        test_order_2 = self.env.ref('sale_delivery_rate.demo_order_2')
        self.test_order_set = test_order_1 + test_order_2

    def test_base_on_rate_get_shipping_price_from_so_no_sales_orders(self):
        """Should return empty list when empty sales order set is provided"""
        test_result = self.test_model.base_on_rate_get_shipping_price_from_so(
            self.env['sale.order'],
        )

        self.assertEqual(test_result, [])

    def test_base_on_rate_get_shipping_price_from_so_no_carrier(self):
        """Should set price to 0.0 for sales orders missing carriers"""
        self.test_order_set[0].carrier_id = False
        test_result = self.test_model.base_on_rate_get_shipping_price_from_so(
            self.test_order_set,
        )

        self.assertEqual(test_result, [0.0, 20.00])

    def test_base_on_rate_get_shipping_price_from_so_no_rates(self):
        """Should set price to 0.0 for sales orders with no rates"""
        self.test_order_set[0].carrier_rate_ids.unlink()
        test_result = self.test_model.base_on_rate_get_shipping_price_from_so(
            self.test_order_set,
        )

        self.assertEqual(test_result, [0.0, 20.00])

    def test_base_on_rate_get_shipping_price_from_so_no_rate_for_carrier(self):
        """Should set price to 0.0 for sales orders with no rate for carrier"""
        self.test_order_set[0].carrier_id = self.env.ref(
            'sale_delivery_rate.demo_carrier_1'
        )
        self.test_order_set[0].carrier_rate_ids.service_id = self.env.ref(
            'sale_delivery_rate.demo_carrier_2',
        )
        test_result = self.test_model.base_on_rate_get_shipping_price_from_so(
            self.test_order_set,
        )

        self.assertEqual(test_result, [0.0, 20.00])

    def test_base_on_rate_get_shipping_price_from_so_correct_rates(self):
        """Should set price based on retail_rate and fall back to rate"""
        self.test_order_set[0].carrier_rate_ids.retail_rate = False
        self.test_order_set[0].carrier_rate_ids.rate = 10.0
        self.test_order_set[1].carrier_rate_ids.retail_rate = 20.0
        test_result = self.test_model.base_on_rate_get_shipping_price_from_so(
            self.test_order_set,
        )

        self.assertEqual(test_result, [10.0, 20.0])

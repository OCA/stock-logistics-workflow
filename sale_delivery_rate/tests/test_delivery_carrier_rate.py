# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestDeliveryCarrierRate(TransactionCase):

    def setUp(self):
        super(TestDeliveryCarrierRate, self).setUp()

        self.test_rate_1 = self.env.ref('sale_delivery_rate.demo_car_rate_1')
        self.test_rate_2 = self.env.ref('sale_delivery_rate.demo_car_rate_2')
        self.test_picking = self.env.ref('sale_delivery_rate.demo_picking_1')

        self.env['stock.picking.rate'].search([]).unlink()

    def test_generate_equiv_picking_rates_picking_not_singleton(self):
        """Should raise correct exception if picking recordset not singleton"""
        test_set_1 = self.env['stock.picking']
        test_picking_copy = self.test_picking.copy()
        test_set_2 = self.test_picking + test_picking_copy

        with self.assertRaises(ValueError):
            self.test_rate_1.generate_equiv_picking_rates(test_set_1)
        with self.assertRaises(ValueError):
            self.test_rate_1.generate_equiv_picking_rates(test_set_2)

    def test_generate_equiv_picking_rates_empty_self(self):
        """Should not create any picking rates if no delivery rates"""
        test_model = self.env['delivery.carrier.rate']
        test_model.generate_equiv_picking_rates(self.test_picking)
        picking_rates = self.env['stock.picking.rate'].search([])

        self.assertEqual(len(picking_rates), 0)

    def test_generate_equiv_picking_rates_accurate_copy(self):
        """Should accurately copy relevant fields in delivery rates"""
        test_set = self.test_rate_1 + self.test_rate_2
        test_set.generate_equiv_picking_rates(self.test_picking)
        picking_rates = self.env['stock.picking.rate'].search([])

        self.assertEqual(
            picking_rates[0].date_generated,
            self.test_rate_1.date_generated,
        )
        self.assertEqual(picking_rates[1].rate, self.test_rate_2.rate)

    def test_generate_equiv_picking_rates_accurate_picking_id(self):
        """Should use ID of provided picking rather than values in rates"""
        alt_picking = self.test_picking.copy()
        self.test_rate_1.picking_id = alt_picking
        self.test_rate_1.generate_equiv_picking_rates(self.test_picking)
        picking_rate = self.env['stock.picking.rate'].search([])

        self.assertEqual(picking_rate.picking_id, self.test_picking)
        self.assertNotEqual(picking_rate.picking_id, alt_picking)

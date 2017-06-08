# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from openerp.tests.common import TransactionCase

MODEL_PATH = 'openerp.addons.sale_delivery_rate.models.delivery_carrier_rate'
MOCK_PATH = MODEL_PATH + '.DeliveryCarrierRate.generate_equiv_picking_rates'


class TestStockMove(TransactionCase):

    def setUp(self):
        super(TestStockMove, self).setUp()

        test_prod = self.env.ref('sale_delivery_rate.demo_stockable_product')
        test_order_line = self.env.ref('sale_delivery_rate.demo_order_line_1')
        self.test_procurement = self.env['procurement.order'].create({
            'company_id': self.env.ref('base.main_company').id,
            'date_planned': '2017-01-01',
            'name': 'Test Procurement',
            'priority': '0',
            'product_id': test_prod.id,
            'product_qty': 1.0,
            'product_uom': self.env.ref('product.product_uom_kgm').id,
            'sale_line_id': test_order_line.id,
        })

        self.test_picking_1 = self.env.ref('sale_delivery_rate.demo_picking_1')
        self.test_picking_2 = self.env.ref('sale_delivery_rate.demo_picking_2')

        self.test_move_1 = self.env['stock.move'].create({
            'company_id': self.env.ref('base.main_company').id,
            'date': '2017-01-01',
            'date_expected': '2017-01-01',
            'location_dest_id': self.env.ref('stock.location_inventory').id,
            'location_id': self.env.ref('stock.location_inventory').id,
            'name': 'Test Stock Move',
            'picking_id': self.test_picking_1.id,
            'procurement_id': self.test_procurement.id,
            'product_id': test_prod.id,
            'product_uom': self.env.ref('product.product_uom_kgm').id,
        })
        self.test_move_2 = self.test_move_1.copy()
        self.test_move_2.picking_id = self.test_picking_2
        self.test_move_set = self.test_move_1 + self.test_move_2

    @mock.patch(MOCK_PATH)
    def test_action_confirm_no_pickings(self, generate_mock):
        """Should not generate rates if moves have no pickings"""
        self.test_move_1.picking_id = False
        self.test_move_2.picking_id = False
        generate_mock.reset_mock()
        self.test_move_set.action_confirm()

        generate_mock.assert_not_called()

    @mock.patch(MOCK_PATH)
    def test_action_confirm_pickings_have_rates(self, generate_mock):
        """Should not generate rates for pickings that already have them"""
        new_rate = self.test_picking_1.dispatch_rate_ids.copy()
        new_rate.picking_id = self.test_picking_2
        generate_mock.reset_mock()
        self.test_move_set.action_confirm()

        generate_mock.assert_not_called()

    @mock.patch(MOCK_PATH)
    def test_action_confirm_pickings_without_sale_order(self, generate_mock):
        """Should not generate rates for pickings without sale order"""
        self.test_move_2.procurement_id = False
        generate_mock.reset_mock()
        self.test_move_set.action_confirm()

        generate_mock.assert_not_called()

    @mock.patch(MOCK_PATH)
    def test_action_confirm_pickings_without_carrier(self, generate_mock):
        """Should not generate rates for pickings with no sale order carrier"""
        self.test_procurement.sale_line_id.order_id.carrier_id = False
        generate_mock.reset_mock()
        self.test_move_set.action_confirm()

        generate_mock.assert_not_called()

    @mock.patch(MOCK_PATH)
    def test_action_confirm_pickings_valid_generate_call(self, generate_mock):
        """Should generate rates with right call when picking has info"""
        generate_mock.reset_mock()
        self.test_move_set.action_confirm()

        generate_mock.assert_called_once_with(self.test_picking_2)

    def test_action_confirm_pickings_valid_correct_copy(self):
        """Should replicate correct sale order rates if picking has info"""
        test_order = self.test_procurement.sale_line_id.order_id
        new_delivery_rate = test_order.carrier_rate_ids.copy()
        new_delivery_rate.service_id = test_order.carrier_id.copy()
        new_delivery_rate.rate = 20
        self.test_move_set.action_confirm()

        test_picking_rate = self.test_picking_2.dispatch_rate_ids
        self.assertEqual(len(test_picking_rate), 1)
        self.assertEqual(test_picking_rate.rate, 10)

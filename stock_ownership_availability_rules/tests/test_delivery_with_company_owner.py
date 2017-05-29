# -*- coding: utf-8 -*-
# Copyright 2014 ALeonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestDeliveryWithCompanyOwner(TransactionCase):

    def setUp(self):
        super(TestDeliveryWithCompanyOwner, self).setUp()
        self.product = self.env.ref('product.product_product_8')
        self.quant = self.env['stock.quant'].create({
            'qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
                self.env.ref('stock.stock_location_customers').id,
        })
        self.move = self.env['stock.move'].create({
            'name': '/',
            'picking_id': self.picking.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
            'product_id': self.product.id,
        })

        self.move.restrict_partner_id = self.env.user.company_id.partner_id

    def test_it_fully_reserves_my_stock(self):
        self.move.product_uom_qty = 80
        self.picking.action_assign()
        self.assertEqual('assigned', self.picking.state)

    def test_it_partially_reserves_stock_with_no_owner(self):
        self.move.product_uom_qty = 150
        self.picking.action_assign()
        self.assertEqual('partially_available', self.picking.state)

    def test_it_doesn_not_reserve_stock_with_different_owner(self):
        self.quant.owner_id = self.env.ref('base.res_partner_1')
        self.move.product_uom_qty = 80
        self.picking.action_assign()
        self.assertEqual('confirmed', self.picking.state)

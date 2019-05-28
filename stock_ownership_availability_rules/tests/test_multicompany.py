# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestMulticompany(TransactionCase):

    def setUp(self):
        super(TestMulticompany, self).setUp()
        self.loc_customers = self.env.ref('stock.stock_location_customers')
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })
        self.user_admin = self.env.ref('base.user_root')
        self.product = self.env.ref('product.product_product_8')
        self.quant = self.env['stock.quant'].create({
            'qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.loc_customers.id,
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

    def test_destination_owner(self):
        quants_before = self.env['stock.quant'].search([
            ('location_id', '=', self.loc_customers.id)])
        self.quant.owner_id = self.env.ref('base.res_partner_1')
        self.move.product_uom_qty = 80
        self.picking.action_assign()
        self.assertEqual('confirmed', self.picking.state)
        # User admin is in Company 2
        self.user_admin.company_id = self.company_2
        self.picking.action_done()
        quants_after = self.env['stock.quant'].search([
            ('location_id', '=', self.loc_customers.id)]) - quants_before
        self.assertEquals(
            1,
            len(quants_after),
        )
        self.assertEquals(
            quants_after.owner_id,
            self.env.user.company_id.partner_id,
        )

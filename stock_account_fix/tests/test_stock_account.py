# -*- coding: utf-8 -*-
#    Copyright (C) Rooms For (Hong Kong) Limited T/A OSCG
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp.tests.common import TransactionCase


class TestStockAccount(TransactionCase):

    def test_owner_false(self):
        count1 = len(self.JournalEntry.search([]))
 
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })
        self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': 1.0,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        picking.action_confirm()
        picking.do_prepare_partial()
        picking.do_transfer()

        count2 = len(self.JournalEntry.search([]))
        self.assertEqual(count1, count2-1)


    def test_owner_true(self):
        count1 = len(self.JournalEntry.search([]))
 
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'owner_id': self.env.ref('base.res_partner_1').id,
        })
        self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': 1.0,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        picking.action_confirm()
        picking.do_prepare_partial()
        picking.do_transfer()

        count2 = len(self.JournalEntry.search([]))
        self.assertEqual(count1, count2)


    def setUp(self):
        super(TestStockAccount, self).setUp()
        self.JournalEntry = self.env['account.move']
        self.product = self.env.ref('product.product_product_36')
        self.product.product_tmpl_id.write({
            'valuation': 'real_time',
            'property_stock_account_input': self.env.ref('account.a_expense').id,
            'property_stock_account_output': self.env.ref('account.cog').id,
        })

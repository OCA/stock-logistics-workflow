#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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


class TestDeliveryWithOwner(TransactionCase):

    def setUp(self):
        super(TestDeliveryWithOwner, self).setUp()
        self.product = self.env.ref('product.product_product_36')
        self.quant = self.env['stock.quant'].create({
            'qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
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

        self.move.restrict_partner_id = self.env.ref('base.res_partner_2')

    def test_it_does_not_reserve_my_stock(self):
        self.move.product_uom_qty = 80
        self.picking.action_assign()
        self.assertEqual('confirmed', self.picking.state)

    def test_it_doesn_not_reserve_stock_with_different_owner(self):
        self.quant.owner_id = self.env.ref('base.res_partner_1')
        self.move.product_uom_qty = 80
        self.picking.action_assign()
        self.assertEqual('confirmed', self.picking.state)

    def test_it_reserves_stock_with_same_owner(self):
        self.quant.owner_id = self.env.ref('base.res_partner_2')
        self.move.product_uom_qty = 80
        self.picking.action_assign()
        self.assertEqual('assigned', self.picking.state)

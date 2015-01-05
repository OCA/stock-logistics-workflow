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


class TestDefaultQuantOwner(TransactionCase):

    def test_it_sets_quant_owner_on_create(self):
        quant = self.Quant.create({
            'qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        self.assertEqual(self.env.user.company_id.partner_id, quant.owner_id)

    def test_it_sets_quant_owner_on_reception(self):
        quant_domain = [('product_id', '=', self.product.id)]
        self.assertFalse(self.Quant.search(quant_domain))

        picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })
        self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
        })
        picking.action_assign()
        picking.action_done()
        created_quant = self.Quant.search(quant_domain)
        self.assertEqual(1, len(created_quant))
        self.assertEqual(self.env.user.company_id.partner_id,
                         created_quant.owner_id)

    def setUp(self):
        super(TestDefaultQuantOwner, self).setUp()
        self.Quant = self.env['stock.quant']
        self.product = self.env.ref('product.product_product_36')

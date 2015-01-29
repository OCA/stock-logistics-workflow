#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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


class TestPickingToPackOps(TransactionCase):

    def test_one_move_takes_owner_from_move(self):
        pick = self._picking_factory(owner=self.partner1)
        pick.move_lines = self._move_factory(product=self.product1,
                                             owner=self.partner2)

        result = pick._prepare_pack_ops(pick, [], {self.product1: 5.0})

        self.assertEqual(1, len(result))
        self.assertEqual(self.partner2.id, result[0]['owner_id'])

    def _picking_factory(self, owner):
        return self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'owner_id': owner.id,
        })

    def _move_factory(self, product, owner, qty=5.0):
        return self.env['stock.move'].create({
            'name': '/',
            'restrict_partner_id': owner.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })

    def setUp(self):
        super(TestPickingToPackOps, self).setUp()
        self.product1 = self.env.ref('product.product_product_33')
        self.product2 = self.env.ref('product.product_product_36')
        self.partner1 = self.env.ref('base.res_partner_1')
        self.partner2 = self.env.ref('base.res_partner_2')

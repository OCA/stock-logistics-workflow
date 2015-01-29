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
        result = self.picking._prepare_pack_ops(self.picking, [],
                                                {self.product: 10})
        self.assertEqual(1, len(result))
        self.assertEqual(self.partner2.id, result[0]['owner_id'])

    def setUp(self):
        super(TestPickingToPackOps, self).setUp()
        self.product = self.env.ref('product.product_product_36')
        self.partner1 = self.env.ref('base.res_partner_1')
        self.partner2 = self.env.ref('base.res_partner_2')

        self.picking = self.env['stock.picking'].new({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'owner_id': self.partner1.id,  # we do not want to use this one
            'move_lines': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 10,
                'restrict_partner_id': self.partner2.id,  # we want this!
            })],
        })

# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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
#
##############################################################################

from openerp.tests.common import TransactionCase


class TestPackagePreparation(TransactionCase):

    def _create_picking(self):
        return self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        })

    def _create_move(self, picking, product, quantity=5.0):
        src_location = self.env.ref('stock.stock_location_stock')
        dest_location = self.env.ref('stock.stock_location_customers')
        return self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product.uom_id.id,
            'location_id': src_location.id,
            'location_dest_id': dest_location.id,
        })

    def _create_preparation(self, pickings):
        return self.env['stock.picking.package.preparation'].create({
            'partner_id': self.partner.id,
            'picking_ids': [(6, 0, pickings.ids)],
            'packaging_id': self.packaging.id,
        })

    def setUp(self):
        super(TestPackagePreparation, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product1 = self.env.ref('product.product_product_33')
        self.product2 = self.env.ref('product.product_product_36')
        self.ul = self.env['product.ul'].create({'name': 'Pallet',
                                                 'type': 'pallet'})
        packaging_tpl = self.env['product.template'].create({'name': 'Pallet'})
        self.packaging = self.env['product.packaging'].create({
            'name': 'Pallet',
            'ul_container': self.ul.id,
            'rows': 1,
            'product_tmpl_id': packaging_tpl.id,
        })
        self.picking_a = self._create_picking()
        self.move_a_1 = self._create_move(self.picking_a,
                                          self.product1)
        self.move_a_2 = self._create_move(self.picking_a,
                                          self.product2)
        self.picking_b = self._create_picking()
        self.move_b_1 = self._create_move(self.picking_b,
                                          self.product1)

    def test_put_in_pack(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        self.assertTrue(prep.package_id)
        self.assertEquals(
            pickings.mapped('move_lines.linked_move_operation_ids.'
                            'operation_id.result_package_id'),
            prep.package_id,
            "All the moves should have a stock.quant.operation with "
            "the same result package"
        )

    def test_done(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()

        prep.action_done()

        self.assertTrue(
            all(picking.state == 'done' for picking in pickings)
        )

    def test_pack_values(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()

        location = self.env.ref('stock.stock_location_customers')
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        package = prep.package_id
        self.assertEquals(package.packaging_id, self.packaging)
        self.assertEquals(package.location_id, location)

    def test_weight(self):
        self.product1.weight = 5  # * 5 units
        self.product2.weight = 2  # * 5 units
        pickings = self.picking_a + self.picking_b
        pickings.action_confirm()
        pickings.force_assign()
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        prep.action_done()
        self.assertEquals(prep.weight, 60)

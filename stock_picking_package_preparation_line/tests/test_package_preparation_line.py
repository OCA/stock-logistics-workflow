# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
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


class TestPackagePreparationLine(TransactionCase):

    def _create_picking(self):
        return self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            })

    def _create_move(self, picking, product, quantity=1.0):
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
            'partner_id': self.partner.id,
            })

    def _create_line(self, preparation, product=None, quantity=0):
        return self.env['stock.picking.package.preparation.line'].create({
            'name': 'test',
            'product_id': product and product.id or False,
            'product_uom_qty': quantity,
            'product_uom': product and product.uom_id.id or False,
            'package_preparation_id': preparation.id,
            })

    def _create_preparation(self, pickings=None):
        values = {'partner_id': self.partner.id, }
        if pickings:
            values.update({'picking_ids': [(6, 0, pickings.ids)], })
        return self.env['stock.picking.package.preparation'].create(values)

    def setUp(self):
        super(TestPackagePreparationLine, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product1 = self.env.ref('product.product_product_33')
        self.product2 = self.env.ref('product.product_product_6')
        self.picking = self._create_picking()
        self.move = self._create_move(self.picking, self.product1)
        self.preparation = self._create_preparation()

    def test_preparation_line_empty(self):
        # ----- Preparation is created withiut lines.
        #       Test if line_ids is empty
        self.assertEquals(len(self.preparation.line_ids), 0)

    def test_auto_line_creation(self):
        # ----- Add a picking in preparation
        #       Test if a preparation line is created for the stock move
        self.preparation.picking_ids = [(6, 0, [self.picking.id, ])]
        self.assertEquals(len(self.preparation.line_ids), 1)

    def test_move_and_picking_create_from_line(self):
        # ----- Add a line in preparation
        #       Test if a stock move and picking are created when "Put in Pack"
        #       is used
        self._create_line(self.preparation, self.product2, 2.0)
        self.preparation.action_put_in_pack()
        self.assertEquals(len(self.preparation.picking_ids), 1)


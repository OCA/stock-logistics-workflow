# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
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
#
from openerp.tests import common


class TestShipmentCreation(common.TransactionCase):
    """ Test creation of a Sale Order and then create shipment based
    on picking created by the Sale Order
    """

    def setUp(self):
        """This setup is repeated on a new transaction for every test.
        No need to duplicate test data then.
        """
        super(TestShipmentCreation, self).setUp()

        # Set warehouse option to pass shipment by Transit
        warehouse = self.env.ref('stock.warehouse0')
        warehouse.delivery_steps = 'ship_transit'

        SO = self.env['sale.order']
        SOL = self.env['sale.order.line']

        so_vals = {
            'partner_id': self.ref('base.res_partner_1'),
        }

        self.so = SO.create(so_vals)

        sol_vals = {
            'order_id': self.so.id,
            'product_id': self.ref('product.product_product_33'),
            'name': "[HEAD-USB] Headset USB",
            'product_uom_qty': 42,
            'product_uom': self.ref('product.product_uom_unit'),
            'price_unit': 65,
        }

        SOL.create(sol_vals)
        self.so.signal_workflow('order_confirm')

        # get move line of single created picking
        self.dest_move = self.so.picking_ids.move_lines

        # Run procurement
        proc_group = self.so.picking_ids.group_id
        proc = proc_group.procurement_ids.filtered(
            lambda rec: rec.state == 'confirmed')
        proc.run()

        self.departure_move = self.env['stock.move'].search(
            [('move_dest_id', '=', self.dest_move.id)])

    def test_create_shiping_from_picking(self):
        """ Try to create a shipment from a picking

        """
        WizardShipmentCreator = self.env['shipment.plan.creator']
        wiz_ctx = {
            'active_model': 'stock.picking',
            'active_ids': self.departure_move.picking_id.ids,
        }
        wiz = WizardShipmentCreator.with_context(wiz_ctx).create({})
        wiz.action_create_shipment()

        shipment = self.departure_move.departure_shipment_id

        self.assertEquals(shipment.departure_move_ids,
                          self.departure_move)
        self.assertEquals(shipment.arrival_move_ids,
                          self.dest_move)

        self.assertEquals(shipment.departure_picking_ids,
                          self.departure_move.picking_id)
        self.assertEquals(shipment.arrival_picking_ids,
                          self.dest_move.picking_id)

        self.assertEquals(shipment.departure_picking_count,
                          1)
        self.assertEquals(shipment.arrival_picking_count,
                          1)

    def test_create_shiping_from_move(self):
        """ Try to create a shipment from a move

        """
        WizardShipmentCreator = self.env['shipment.plan.creator']
        wiz_ctx = {
            'active_model': 'stock.move',
            'active_ids': self.departure_move.ids,
        }
        wiz = WizardShipmentCreator.with_context(wiz_ctx).create({})
        wiz.action_create_shipment()

        shipment = self.departure_move.departure_shipment_id

        self.assertEquals(shipment.departure_move_ids,
                          self.departure_move)
        self.assertEquals(shipment.arrival_move_ids,
                          self.dest_move)

        self.assertEquals(shipment.departure_picking_ids,
                          self.departure_move.picking_id)
        self.assertEquals(shipment.arrival_picking_ids,
                          self.dest_move.picking_id)

        self.assertEquals(shipment.departure_picking_count,
                          1)
        self.assertEquals(shipment.arrival_picking_count,
                          1)

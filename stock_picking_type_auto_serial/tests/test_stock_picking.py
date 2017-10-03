# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestStockPicking(TransactionCase):

    def setUp(self):
        super(TestStockPicking, self).setUp()

        self.picking_model = self.env['stock.picking']
        self.move_model = self.env['stock.move']

        # warehouse and picking types
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.picking_type_in = self.env.ref('stock.chi_picking_type_in')
        self.picking_type_int = self.env.ref('stock.chi_picking_type_out')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')

        # products
        self.product_9 = self.env.ref('product.product_product_9')
        self.product_8 = self.env.ref('product.product_product_8')
        self.product_10 = self.env.ref('product.product_product_10')

        # supplier
        self.supplier = self.env.ref('base.res_partner_1')

        self.picking = self.picking_model.with_context(
            default_picking_type_id=self.picking_type_in.id).create({
                'partner_id': self.supplier.id,
                'location_id': self.supplier_location.id})

    def test_1(self):
        """
        Test Case:
            - A picking with in picking operation (i.e stock_picking_type.code
            = 'supplier').
            - One stock.move line with product_qty = 1 and.
            - the picking type has the flag autmatic serial generation on.
            - the tracking on the product is set to serial.
        Expected result:
            - an automatic serial number is generated. and a lot is created
            using that number.
        """

        self.picking_type_in.automatic_serial_generation = True
        self.product_9.tracking = 'serial'
        self.product_9.automatic_serial_generation = True

        self.move_model.create(
            dict(product_id=self.product_9.id,
                 picking_id=self.picking.id,
                 name=self.product_9.display_name,
                 picking_type_id=self.picking_type_in.id,
                 product_uom_qty=1.0,
                 location_id=self.supplier_location.id,
                 location_dest_id=self.picking_type_in.
                 default_location_dest_id.id,
                 product_uom=self.product_9.uom_id.id))

        # run the whole reception process
        self.picking.action_confirm()
        self.assertEqual(len(self.picking.pack_operation_ids), 1)
        self.picking.pack_operation_ids.qty_done = \
            self.picking.pack_operation_ids.product_qty
        self.picking.do_transfer()

        self.assertEqual(self.picking.state, 'done')

    def test_2(self):
        """
        Test Case:
            - A picking with in picking operation.
            - One stock.move line with product_qty = 1.
            - the picking type has the flag autmatic serial generation off.
            - the tracking on the product is set to serial.
        Expected result:
            - no automatic serial is created, the serial has to be added
            manually.
        """
        self.product_9.tracking = 'serial'
        self.product_9.automatic_serial_generation = True

        self.move_model.create(
            dict(product_id=self.product_9.id,
                 picking_id=self.picking.id,
                 name=self.product_9.display_name,
                 picking_type_id=self.picking_type_in.id,
                 product_uom_qty=1.0,
                 location_id=self.supplier_location.id,
                 location_dest_id=self.picking_type_in.
                 default_location_dest_id.id,
                 product_uom=self.product_9.uom_id.id))

        # run the whole reception process
        self.picking.action_confirm()
        with self.assertRaises(UserError):
            self.picking.do_transfer()

    def test_3(self):
        """
        Test Case:
            - A picking with in picking operation.
            - Multiple stock.move line.
            - the picking type has the flag autmatic serial generation on.
            - some products have tracking set to serial, some to none and
            some to lot.
        Expected result:
            - Only product with serial have an automatic lot generated.
        """

        self.picking_type_in.automatic_serial_generation = True
        self.product_8.tracking = 'lot'
        self.product_9.tracking = 'none'
        self.product_10.tracking = 'serial'
        self.product_10.automatic_serial_generation = True

        self.move_model.create(
            dict(product_id=self.product_8.id,
                 picking_id=self.picking.id,
                 name=self.product_8.display_name,
                 picking_type_id=self.picking_type_in.id,
                 product_uom_qty=1.0,
                 location_id=self.supplier_location.id,
                 location_dest_id=self.picking_type_in.
                 default_location_dest_id.id,
                 product_uom=self.product_9.uom_id.id))

        self.move_model.create(
            dict(product_id=self.product_9.id,
                 picking_id=self.picking.id,
                 name=self.product_9.display_name,
                 picking_type_id=self.picking_type_in.id,
                 product_uom_qty=1.0,
                 location_id=self.supplier_location.id,
                 location_dest_id=self.picking_type_in.
                 default_location_dest_id.id,
                 product_uom=self.product_9.uom_id.id))

        self.move_model.create(
            dict(product_id=self.product_10.id,
                 picking_id=self.picking.id,
                 name=self.product_10.display_name,
                 picking_type_id=self.picking_type_in.id,
                 product_uom_qty=1.0,
                 location_id=self.supplier_location.id,
                 location_dest_id=self.picking_type_in.
                 default_location_dest_id.id,
                 product_uom=self.product_10.uom_id.id))

        self.picking.action_confirm()
        self.assertEqual(len(self.picking.pack_operation_ids), 3)

        product_10_pack_ops = [
            x for x in self.picking.pack_operation_ids if
            x.product_id == self.product_10]

        product_10_pack_ops[0].qty_done = product_10_pack_ops[0].product_qty
        # The do transfer should fail because no serial is generated
        # automatically for product with lot tracking
        with self.assertRaises(UserError), self.cr.savepoint():
            self.picking.do_transfer()

        product_8_pack_ops = [
            x for x in self.picking.pack_operation_ids if
            x.product_id == self.product_8]
        lot = self.env['stock.production.lot'].create({
            'name': 'Test 1',
            'product_id': self.product_8.id,
        })
        product_8_pack_ops[0].pack_lot_ids = [(0, 0, {
            'lot_id': lot, 'qty': product_8_pack_ops[0].product_qty})]

        self.picking.do_transfer()

    def test_4(self):
        """
        Test Case:
            - create picking with in operation.
            - One stock move with product_qty > 1.
            - the picking type has the flag autmatic serial generation on.
            - The product has tracking set to serial.
        Expected result:
            - an automatic serial number is generated only the first operation,
            in the second operation no serial is generated.
        """
        self.warehouse.reception_steps = 'two_steps'

        self.picking_type_in.automatic_serial_generation = True
        self.product_9.tracking = 'serial'
        self.product_9.automatic_serial_generation = True

        self.move_model.create(
            dict(product_id=self.product_9.id,
                 picking_id=self.picking.id,
                 name=self.product_9.display_name,
                 picking_type_id=self.picking_type_in.id,
                 product_uom_qty=2.0,
                 location_id=self.supplier_location.id,
                 location_dest_id=self.picking_type_in.
                 default_location_dest_id.id,
                 product_uom=self.product_9.uom_id.id))

        # run the whole reception process
        self.picking.action_confirm()
        self.assertEqual(len(self.picking.pack_operation_ids), 1)
        self.picking.pack_operation_ids.qty_done = \
            self.picking.pack_operation_ids.product_qty
        self.picking.do_transfer()

        self.assertEqual(len(self.picking.pack_operation_ids), 1)
        self.assertTrue(len(self.picking.pack_operation_ids.pack_lot_ids), 2)

        second_operation = self.picking_model.search(
            [('group_id', '=', self.picking.group_id.id),
             ('picking_type_id', '=', self.warehouse.int_type_id.id)])
        self.assertTrue(second_operation)
        with self.assertRaises(UserError):
            self.picking.do_transfer()

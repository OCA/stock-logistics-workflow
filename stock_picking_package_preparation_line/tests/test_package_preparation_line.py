# -*- coding: utf-8 -*-
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPackagePreparationLine(TransactionCase):

    def _create_picking(self):
        return self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.src_location.id,
            'location_dest_id': self.dest_location.id,
            })

    def _create_move(self, picking, product, quantity=1.0):
        return self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product.uom_id.id,
            'location_id': self.src_location.id,
            'location_dest_id': self.dest_location.id,
            'partner_id': self.partner.id,
            })

    def _create_line(self, preparation, product=None, quantity=0):
        return self.env['stock.picking.package.preparation.line'].create({
            'name': 'test',
            'product_id': product and product.id or False,
            'product_uom_qty': quantity,
            'product_uom_id': product and product.uom_id.id or False,
            'package_preparation_id': preparation.id,
            })

    def _create_preparation(self, pickings=None):
        values = {'partner_id': self.partner.id, }
        if pickings:
            values.update({'picking_ids': [(6, 0, pickings.ids)], })
        return self.env['stock.picking.package.preparation'].create(values)

    def setUp(self):
        super(TestPackagePreparationLine, self).setUp()
        self.src_location = self.env.ref('stock.stock_location_stock')
        self.dest_location = self.env.ref('stock.stock_location_customers')
        self.partner = self.env.ref('base.res_partner_2')
        self.product1 = self.env.ref('product.product_product_33')
        self.product2 = self.env.ref('product.product_product_6')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.picking_type_out.default_location_dest_id = self.dest_location.id
        self.picking = self._create_picking()
        self.move = self._create_move(self.picking, self.product1)
        self.preparation = self._create_preparation()

    def test_preparation_line_empty(self):
        # Preparation is created without lines.
        # Test if line_ids is empty
        self.assertEquals(len(self.preparation.line_ids), 0)

    def test_auto_line_creation(self):
        # Add a picking in preparation
        # Test if a preparation line is created for the stock move
        self.preparation.picking_ids = [(6, 0, [self.picking.id, ])]
        self.assertEquals(len(self.preparation.line_ids), 1)

    def test_move_and_picking_create_from_line(self):
        # Add a line in preparation
        # Test if a stock move and picking are created when "Put in Pack"
        # is used
        self._create_line(self.preparation, self.product2, 2.0)
        self.preparation.action_put_in_pack()
        self.assertEquals(len(self.preparation.picking_ids), 1)
        # Check if stock move and package preparation line have the some
        # name
        self.assertEquals(
            self.preparation.picking_ids[0].move_lines[0].name,
            self.preparation.line_ids[0].name
            )
        # Check if stock move and package preparation line have the some
        # quantity
        self.assertEquals(
            self.preparation.picking_ids[0].move_lines[0].product_uom_qty,
            self.preparation.line_ids[0].product_uom_qty
            )

    def test_change_qty_on_preparation_line(self):
        # Create a Preparation Line, then change qty on line
        # Test if qty on stock move are equals to qty on Preparation Line
        self._create_line(self.preparation, self.product2, 3.0)
        self.preparation.action_put_in_pack()
        # Modify qty on line
        test_line = self.preparation.line_ids[0]
        test_line.product_uom_qty = 4.0
        self.assertEquals(test_line.product_uom_qty,
                          test_line.move_id.product_qty)

    def test_change_on_stock_move(self):
        # Change information on a stock move related with package
        # preparation line and check if this line has new information
        self._create_line(self.preparation, self.product2, 2.0)
        self.preparation.action_put_in_pack()
        # Change stock move name
        self.preparation.line_ids[0].move_id.name = 'Changed for test'
        self.assertEquals(self.preparation.line_ids[0].name,
                          self.preparation.line_ids[0].move_id.name)

    def test_change_stock_move_quantity(self):
        # Create a package preparation line with relative stock move
        # to test a change on stock move quantity
        self._create_line(self.preparation, self.product2, 2.0)
        self.preparation.action_put_in_pack()
        self.preparation.line_ids[0].move_id.product_uom_qty = 3.0
        self.assertEquals(self.preparation.line_ids[0].product_uom_qty, 3.0)

    def test_package_with_description_line_and_product_line(self):
        # Create a package prepartion with 2 line one of them is a
        # description line only to test picking have only one move
        self._create_line(self.preparation, self.product2, 1.0)
        self._create_line(self.preparation, None, 0)
        self.preparation.action_put_in_pack()
        # Check have only one move line
        self.assertEqual(len(self.preparation.picking_ids[0].move_lines), 1)
        # Check product on move line is the same
        self.assertEqual(
            self.preparation.picking_ids[0].move_lines[0].product_id,
            self.product2)

    def test_remove_picking_from_package_preparation(self):
        # Remove picking from package preparation to test what happens
        # to package preparation line
        self.picking2 = self._create_picking()
        self._create_move(self.picking2, self.product2)
        self.preparation.picking_ids = [
            (6, 0, [self.picking.id, self.picking2.id])]
        self.preparation.picking_ids = [(3, self.picking.id)]
        self.assertEquals(len(self.preparation.line_ids), 1)

    def test_standard_flow_with_detail_with_lot(self):
        # Test a standard flow of a package preparation but add a lot
        # on detail
        # Create a lot
        lot = self.env['stock.production.lot'].create({
            'name': self.product1.name,
            'product_id': self.product1.id,
            })
        # Add a line in preparation with lot
        line = self._create_line(self.preparation, self.product1, 2.0)
        # Assign lot to line
        line.lot_id = lot.id
        # Put In Pack
        self.preparation.action_put_in_pack()
        # Check operations
        self.assertEqual(len(self.preparation.pack_operation_ids), 1)
        # Check Lot on Operation
        self.assertEqual(
            self.preparation.pack_operation_ids[0].pack_lot_ids[0].lot_id.id,
            lot.id)
        # Package Done
        self.preparation.action_done()
        # Check lot on quants of stock move
        self.assertEqual(
            self.preparation.picking_ids[0].move_lines[0].
            quant_ids[0].lot_id.id,
            lot.id)
        self.assertEqual(
            self.preparation.picking_ids[0].move_lines[0].
            quant_ids[1].lot_id.id,
            lot.id)

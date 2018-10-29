# Copyright 2015 Francesco Apruzzese - Apulia Software srl
# Copyright 2015-2018 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPackagePreparationLine(TransactionCase):

    def _create_picking(self):
        return self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.src_location.id,
            'location_dest_id': self.dest_location.id,
            })

    def _create_move(self, picking, product, quantity=1.0):
        self.env['stock.quant']._update_available_quantity(
            self.product1, self.src_location, quantity)
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

    def _create_line(self, preparation, product=None, quantity=0.0,
                     lot_id=None):
        self.env['stock.quant']._update_available_quantity(
            self.product1, self.src_location, quantity, lot_id=lot_id)
        return self.env['stock.picking.package.preparation.line'].create({
            'name': 'test',
            'product_id': product and product.id or False,
            'product_uom_qty': quantity,
            'product_uom_id': product and product.uom_id.id or False,
            'package_preparation_id': preparation.id,
            'note': 'note',
            'lot_id': lot_id.id if lot_id else False
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
        self.product1 = self.env.ref('product.product_product_16')
        self.product2 = self.env.ref('product.product_product_17')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.picking_type_out.default_location_dest_id = self.dest_location.id
        self.picking = self._create_picking()
        self.move = self._create_move(self.picking, self.product1)
        self.preparation = self._create_preparation()

    def test_preparation_line_empty(self):
        # Preparation is created without lines.
        # Test if line_ids is empty
        self.assertEqual(len(self.preparation.line_ids), 0)

    def test_auto_line_creation(self):
        # Add a picking in preparation
        # Test if a preparation line is created for the stock move
        self.preparation.picking_ids = [(6, 0, [self.picking.id, ])]
        self.assertEqual(len(self.preparation.line_ids), 1)

    def test_line_product_onchange(self):
        line = self._create_line(self.preparation, self.product2, 2.0)

        # Test onchange
        line._onchange_product_id()
        self.assertEqual(self.product2.display_name, line.name)
        self.assertEqual(self.product2.uom_id, line.product_uom_id)

    def test_move_and_picking_create_from_line(self):
        # Add a line in preparation
        # Test if a stock move and picking are created when "Put in Pack"
        # is used
        self._create_line(self.preparation, self.product2, 2.0)
        self.preparation.action_put_in_pack()
        self.assertEqual(len(self.preparation.picking_ids), 1)
        # Check if stock move and package preparation line have the some
        # name
        self.assertEqual(
            self.preparation.picking_ids[0].move_lines[0].name,
            self.preparation.line_ids[0].name
            )
        # Check if stock move and package preparation line have the some
        # quantity
        self.assertEqual(
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
        self.assertEqual(test_line.product_uom_qty,
                         test_line.move_id.product_qty)

    def test_change_on_stock_move(self):
        # Change information on a stock move related with package
        # preparation line and check if this line has new information
        self._create_line(self.preparation, self.product2, 2.0)
        self.preparation.action_put_in_pack()
        # Change stock move name
        self.preparation.line_ids[0].move_id.name = 'Changed for test'
        self.assertEqual(self.preparation.line_ids[0].name,
                         self.preparation.line_ids[0].move_id.name)

    def test_change_stock_move_quantity(self):
        # Create a package preparation line with relative stock move
        # to test a change on stock move quantity
        self._create_line(self.preparation, self.product2, 2.0)
        self.preparation.action_put_in_pack()
        self.preparation.line_ids[0].move_id.product_uom_qty = 3.0
        self.assertEqual(self.preparation.line_ids[0].product_uom_qty, 3.0)

    def test_package_with_description_line_and_product_line(self):
        # Create a package preparation with 2 line one of them is a
        # description line only to test picking have only one move
        self._create_line(self.preparation, self.product2, 1.0)
        self._create_line(self.preparation, quantity=0)
        self.preparation.action_put_in_pack()
        # Check have only one move line
        self.assertEqual(len(self.preparation.picking_ids[0].move_lines), 1)
        # Check product on move line is the same
        self.assertEqual(
            self.preparation.picking_ids[0].move_lines[0].product_id,
            self.product2)
        for line in self.preparation.line_ids:
            self.assertEqual(line.note, 'note')

    def test_remove_picking_from_package_preparation(self):
        # Remove picking from package preparation to test what happens
        # to package preparation line
        self.picking2 = self._create_picking()
        self._create_move(self.picking2, self.product2)
        self.preparation.picking_ids = [
            (6, 0, [self.picking.id, self.picking2.id])]
        self.preparation.picking_ids = [(3, self.picking.id)]
        self.assertEqual(len(self.preparation.line_ids), 1)

    def test_standard_flow_with_detail_with_lot(self):
        # Test a standard flow of a package preparation but add a lot
        # on detail
        # Create a lot
        lot = self.env['stock.production.lot'].create({
            'name': self.product1.name,
            'product_id': self.product1.id,
            })
        self.product1.tracking = 'lot'
        # Add a line in preparation with lot
        quantity = 2.0
        self._create_line(self.preparation, self.product1, quantity,
                          lot_id=lot)
        # Put In Pack
        self.preparation.action_put_in_pack()
        # Check operations
        self.assertEqual(len(self.preparation.move_line_ids), 1)
        # Check Lot on Operation
        self.assertEqual(
            self.preparation.move_line_ids[0].lot_id.id,
            lot.id)
        # Package Done
        src_quant = self.env['stock.quant']._gather(
            product_id=self.product1,
            location_id=self.src_location,
            lot_id=lot)
        self.assertTrue(src_quant.exists())
        self.assertEqual(src_quant.quantity, quantity)
        self.preparation.action_done()
        # Check lot of stock move line
        self.assertEqual(
            self.preparation.picking_ids[0].move_line_ids[0].lot_id.id,
            lot.id)
        dst_quant = self.env['stock.quant']._gather(
            product_id=self.product1,
            location_id=self.dest_location,
            lot_id=lot)
        # Check quant has moved
        self.assertFalse(src_quant.exists())
        self.assertEqual(dst_quant.quantity, quantity)

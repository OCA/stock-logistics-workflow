# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
###############################################################################
#    Coded by: Sergio Ernesto Tostado Sánchez (sergio@vauxoo.com)
###############################################################################
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
###############################################################################

from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm


class TestUnicity(TransactionCase):

    """
    This test will prove the next cases to procure the
    module unicity:
    - Test 1: Can't be created two Serial Numbers with the same name
    """

    def setUp(self):
        super(TestUnicity, self).setUp()
        self.stock_production_lot_obj = self.env['stock.production.lot']
        self.stock_picking_type_obj = self.env['stock.picking.type']
        self.stock_picking_obj = self.env['stock.picking']
        self.product_obj = self.env['product.product']
        self.stock_move_obj = self.env['stock.move']
        self.product_uom_obj = self.env['product.uom']
        self.stock_location_obj = self.env['stock.location']

    # '''
    # #@mute()
    # def test_1_creating_two_equal_serial_numbers(self):
        # """
        # Test 1. Creating 2 equal serial numbers
        # """
        # product_id = self.env.ref('product_unique_serial.product_demo_1')
        # print product_id
        # sucessful = False
        # lot_data = {'ref': '86137801852519', 'product_id': product_id.id}
        # self.stock_production_lot_obj.create(lot_data)
        # try:
        #    self.stock_production_lot_obj.create(lot_data)
        # except Exception:
        #    import pdb;pdb.set_trace()
        #    sucessful = True
        # self.assertTrue(sucessful, "ERROR: The module can create duplicated"\
        #    " serial numbers, which is a problem that should be attended...")
    # '''

    def create_stock_moves(self, moves_data, picking_type_xml_id):
        """ Returns a list of ids for each created stock.move """
        stock_move_ids = []
        for move in moves_data:
            stock_move_ids.append(
                self.stock_move_obj.with_context(
                    default_picking_type_id=self.env.ref(
                        picking_type_xml_id).id).\
                create(move).id)
        return stock_move_ids

    def create_stock_picking(self, moves_data, picking_data,
                              picking_type_xml_id):
        """ Returns the stock.picking object """
        move_lines = self.create_stock_moves(moves_data, picking_type_xml_id)
        picking_type = self.env.ref(picking_type_xml_id)
        picking_data.update(
            {'move_lines': [(6, 0, move_lines)],
             'picking_type_id': picking_type.id})
        return self.stock_picking_obj.create(picking_data)

    def transfer_picking(self, picking_instance, serial_number):
        """ Creates a wizard to transfer the picking given like parameter """
        # Marking the picking as Todo
        picking_instance.action_confirm()
        if picking_instance.state == 'confirmed':
            # Checking availability
            picking_instance.action_assign()
        # Transfering picking
        transfer_details = picking_instance.do_enter_transfer_details()
        wizard_for_transfer = self.env[transfer_details.get('res_model')].\
            browse(transfer_details.get('res_id'))
        for transfer_item in wizard_for_transfer.item_ids:
            transfer_item.lot_id = self.env.ref(
                serial_number).id
        # Executing the picking transfering
        wizard_for_transfer.do_detailed_transfer()

    def test_1_1product_1serialnumber_2p_in(self):
        """
        Test 1. Creating 2 pickings with 1 product for the same serial number,
        in the receipts scope, with the next form:
        - Picking 1
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||      1     ||      001       ||
        =============================================
        - Picking 2
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||      1     ||      001       ||
        =============================================
        Warehouse: Your Company
        """
        test_passed = False
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        unit_of_measure = self.env.ref('product.product_uom_unit')
        stock_move_data = {
            'product_id': product.id,
            'product_uom': unit_of_measure.id,
            'product_uom_qty': 1.0,
            'name': "Stock move for %s for test purposes" % product.name
        }
        # Creating the picking
        picking_data_1 = {
            'name': 'Test Picking 1',
            'move_type': 'direct',
            'priority': '1'
        }
        picking_data_2 = {
            'name': 'Test Picking 2',
            'move_type': 'direct',
            'priority': '1'
        }
        picking_1 = self.create_stock_picking(
            [stock_move_data], picking_data_1, 'stock.picking_type_in')
        picking_2 = self.create_stock_picking(
            [stock_move_data], picking_data_2, 'stock.picking_type_in')
        # Executing the wizard for pickings transfering
        self.transfer_picking(
            picking_1,
            'product_unique_serial.serial_number_demo_1')
        try:
            self.transfer_picking(
                picking_2,
                'product_unique_serial.serial_number_demo_1')
        except except_orm, msg:
            print msg
            test_passed = True
        self.assertTrue(
            test_passed,
            "ERROR: The module can transfer pickings-"
            "receipt with a product that has a quantity >1 with a lot_id")

    def test_2_1product_1serialnumber_2p_out(self):
        """
        Test 2. Creating 2 pickings with 1 product for the same serial number,
        in the delivery orders scope, with the next form:
        - Picking 1
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||      1     ||      001       ||
        =============================================
        - Picking 2
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||      1     ||      001       ||
        =============================================
        Warehouse: Your Company
        """
        test_passed = False
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        unit_of_measure = self.env.ref('product.product_uom_unit')
        stock_move_data = {
            'product_id': product.id,
            'product_uom': unit_of_measure.id,
            'product_uom_qty': 1.0,
            'name': "Stock move for %s for test purposes" % product.name
        }
        # Creating the picking
        picking_data_1 = {
            'name': 'Test Picking 1',
            'move_type': 'direct',
            'priority': '1'
        }
        picking_data_2 = {
            'name': 'Test Picking 2',
            'move_type': 'direct',
            'priority': '1'
        }
        picking_1 = self.create_stock_picking(
            [stock_move_data], picking_data_1, 'stock.picking_type_out')
        picking_2 = self.create_stock_picking(
            [stock_move_data], picking_data_2, 'stock.picking_type_out')
        # Executing the wizard for pickings transfering
        self.transfer_picking(
            picking_1,
            'product_unique_serial.serial_number_demo_2')
        try:
            self.transfer_picking(
                picking_2,
                'product_unique_serial.serial_number_demo_2')
        except except_orm, msg:
            print msg
            test_passed = True
        self.assertTrue(
            test_passed,
            "ERROR: The module can transfer pickings-delivery-order "
            "with a product that has a quantity >1 with a lot_id")

    '''
    def test_3_many_products_one_serial_number_out(self):
        """
        Test 3. Creating a pick with 2 products for the same serial number,
        in the delivery orders scope, with the next form:
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||     > 1    ||      001       ||
        =============================================
        Warehouse: Your Company
        """
        available_serial_numbers = None
        test_passed = False
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        unit_of_measure = self.env.ref('product.product_uom_unit')
        stock_move_data = {
            'product_id': product.id,
            'product_uom': unit_of_measure.id,
            'product_uom_qty': 50.0,
            'name': "Stock move for %s for test purposes" % product.name
        }
        stock_move_rec = self.stock_move_obj.with_context(
            default_picking_type_id=self.env.ref('stock.picking_type_out').id
            ).create(stock_move_data)
        # Creating the picking
        picking_type = self.env.ref('stock.picking_type_out')
        picking_data = {
            'name': 'Test Picking',
            'move_type': 'direct',
            'picking_type_id': picking_type.id,
            'priority': '1',
            'move_lines': [(6, 0, [stock_move_rec.id])]
        }
        picking = self.stock_picking_obj.create(picking_data)
        # Marking the picking as Todo
        picking.action_confirm()
        # Transfering picking
        transfer_details = picking.do_enter_transfer_details()
        wizard_for_transfer = self.env[transfer_details.get('res_model')].\
            browse(transfer_details.get('res_id'))
        for transfer_item in wizard_for_transfer.item_ids:
            transfer_item.lot_id = self.env.ref(
                'product_unique_serial.serial_number_demo_1').id
        # Executing the picking transfering
        try:
            wizard_for_transfer.do_detailed_transfer()
        except except_orm, msg:
            print msg
            test_passed = True
        self.assertTrue(
            test_passed,
            "ERROR: The module can transfer pickings-"
            "delivery with a product that has a quantity >1 with a lot_id")

    def test_4_chi_many_products_one_serial_number_in(self):
        """
        Test 4. Creating a pick with 2 products for the same serial number,
        in the receipts scope, with the next form:
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||     > 1    ||      001       ||
        =============================================
        Warehouse: Chicago
        """
        available_serial_numbers = None
        test_passed = False
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        unit_of_measure = self.env.ref('product.product_uom_unit')
        stock_move_data = {
            'product_id': product.id,
            'product_uom': unit_of_measure.id,
            'product_uom_qty': 50.0,
            'name': "Stock move for %s for test purposes" % product.name
        }
        stock_move_rec = self.stock_move_obj.with_context(
            default_picking_type_id=self.env.ref(
                'stock.chi_picking_type_in').id
            ).create(stock_move_data)
        # Creating the picking
        picking_type = self.env.ref('stock.chi_picking_type_in')
        picking_data = {
            'name': 'Test Picking',
            'move_type': 'direct',
            'picking_type_id': picking_type.id,
            'priority': '1',
            'move_lines': [(6, 0, [stock_move_rec.id])]
        }
        picking = self.stock_picking_obj.create(picking_data)
        # Marking the picking as Todo
        picking.action_confirm()
        # Transfering picking
        transfer_details = picking.do_enter_transfer_details()
        wizard_for_transfer = self.env[transfer_details.get('res_model')].\
            browse(transfer_details.get('res_id'))
        for transfer_item in wizard_for_transfer.item_ids:
            transfer_item.lot_id = self.env.ref(
                'product_unique_serial.serial_number_demo_1').id
        # Executing the picking transfering
        try:
            wizard_for_transfer.do_detailed_transfer()
        except except_orm, msg:
            print msg
            test_passed = True
        self.assertTrue(
            test_passed,
            "ERROR: The module can transfer pickings-"
            "receipts with a product that has a quantity >1 with a lot_id")

    def test_5_chi_many_products_one_serial_number_out(self):
        """
        Test 5. Creating a pick with 2 products for the same serial number,
        in the delivery orders scope, with the next form:
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||     > 1    ||      001       ||
        =============================================
        Warehouse: Chicago
        """
        available_serial_numbers = None
        test_passed = False
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        unit_of_measure = self.env.ref('product.product_uom_unit')
        stock_move_data = {
            'product_id': product.id,
            'product_uom': unit_of_measure.id,
            'product_uom_qty': 50.0,
            'name': "Stock move for %s for test purposes" % product.name
        }
        stock_move_rec = self.stock_move_obj.with_context(
            default_picking_type_id=self.env.ref(
                'stock.chi_picking_type_out').id
            ).create(stock_move_data)
        # Creating the picking
        picking_type = self.env.ref('stock.chi_picking_type_out')
        picking_data = {
            'name': 'Test Picking',
            'move_type': 'direct',
            'picking_type_id': picking_type.id,
            'priority': '1',
            'move_lines': [(6, 0, [stock_move_rec.id])]
        }
        picking = self.stock_picking_obj.create(picking_data)
        # Marking the picking as Todo
        picking.action_confirm()
        # Transfering picking
        transfer_details = picking.do_enter_transfer_details()
        wizard_for_transfer = self.env[transfer_details.get('res_model')].\
            browse(transfer_details.get('res_id'))
        for transfer_item in wizard_for_transfer.item_ids:
            transfer_item.lot_id = self.env.ref(
                'product_unique_serial.serial_number_demo_1').id
        # Executing the picking transfering
        try:
            wizard_for_transfer.do_detailed_transfer()
        except except_orm, msg:
            print msg
            test_passed = True
        self.assertTrue(
            test_passed,
            "ERROR: The module can transfer pickings-"
            "delivery with a product that has a quantity >1 with a lot_id")

    def test_6_many_products_one_serial_number_int(self):
        """
        Test 2. Creating a pick with 2 products for the same serial number,
        in the internal scope, with the next form:
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||     > 1    ||      001       ||
        =============================================
        Warehouse: Your Company
        """
        available_serial_numbers = None
        test_passed = False
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        unit_of_measure = self.env.ref('product.product_uom_unit')
        stock_move_data = {
            'product_id': product.id,
            'product_uom': unit_of_measure.id,
            'product_uom_qty': 50.0,
            'name': "Stock move for %s for test purposes" % product.name
        }
        stock_move_rec = self.stock_move_obj.with_context(
            default_picking_type_id=self.env.ref(
                'stock.picking_type_internal').id
            ).create(stock_move_data)
        # Creating the picking
        picking_type = self.env.ref('stock.picking_type_internal')
        picking_data = {
            'name': 'Test Picking',
            'move_type': 'direct',
            'picking_type_id': picking_type.id,
            'priority': '1',
            'move_lines': [(6, 0, [stock_move_rec.id])]
        }
        picking = self.stock_picking_obj.create(picking_data)
        # Marking the picking as Todo
        picking.action_confirm()
        # Checking availability
        picking.action_assign()
        # Transfering picking
        transfer_details = picking.do_enter_transfer_details()
        #~ wizard_for_transfer = self.env[transfer_details.get('res_model')].\
            #~ browse(transfer_details.get('res_id'))
        #~ for transfer_item in wizard_for_transfer.item_ids:
            #~ transfer_item.lot_id = self.env.ref(
                #~ 'product_unique_serial.serial_number_demo_1').id
        #~ # Executing the picking transfering
        #~ try:
            #~ wizard_for_transfer.do_detailed_transfer()
        #~ except except_orm, msg:
            #~ print msg
            #~ test_passed = True
        #~ self.assertTrue(
            #~ test_passed,
            #~ "ERROR: The module can transfer pickings-"
            #~ "internal with a product that has a quantity >1 with a lot_id")
    '''

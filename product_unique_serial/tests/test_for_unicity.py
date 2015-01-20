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

from copy import deepcopy

from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm
from openerp.tools import mute_logger
from psycopg2 import IntegrityError


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

    def create_stock_picking(self, moves_data, picking_data, picking_type):
        """ Returns the stock.picking object, with his respective created
            created stock.move lines """
        # Require deepcopy for clone dict into list items
        moves_data_copy = deepcopy(moves_data)
        picking_data_copy = picking_data.copy()
        stock_move_ids = []
        default_product_data = None
        for move_n in moves_data_copy:
            # Getting the qty for the stock.move
            qty = move_n.get('qty')
            del move_n['qty']
            # Getting default data through product_id onchange
            if 'source_loc' in move_n.keys()\
                    and 'destination_loc' in move_n.keys():
                default_product_data = self.stock_move_obj.onchange_product_id(
                    prod_id=move_n.get('product_id'),
                    loc_id=move_n.get('source_loc'),
                    loc_dest_id=move_n.get('destination_loc'))
                del move_n['source_loc']
                del move_n['destination_loc']
            else:
                default_product_data = self.stock_move_obj.onchange_product_id(
                    move_n.get('product_id'))
            move_n.update(default_product_data.get('value'))
            # Getting default data through product_uom_qty onchange
            default_qty_data = self.stock_move_obj.onchange_quantity(
                move_n.get('product_id'),
                qty,
                default_product_data.get('product_uom'),
                default_product_data.get('product_uos'))
            default_qty_data['value'].update({'product_uom_qty': qty})
            move_n.update(default_qty_data.get('value'))
            # Getting the new stock.move id
            move_created = self.stock_move_obj.with_context(
                default_picking_type_id=picking_type.id).create(move_n)
            stock_move_ids.append(move_created.id)
        # Creating picking
        picking_data_copy.update({
            'move_lines': [(6, 0, stock_move_ids)],
            # TODO: Uncomment when fix current context bug
            # 'move_lines': [(0, 0, moves_data_copy)],
            # and remove move_created line
            'picking_type_id': picking_type.id})
        return self.stock_picking_obj.create(picking_data_copy)

    def transfer_picking(self, picking_instance, serial_number=None):
        """ Creates a wizard to transfer the picking given like parameter """
        # Marking the picking as Todo
        picking_instance.action_confirm()
        if picking_instance.state == 'confirmed':
            # Checking availability
            picking_instance.action_assign()
        if picking_instance.state == 'assigned':
            # Transfering picking
            transfer_details = picking_instance.do_enter_transfer_details()
            wizard_for_transfer = self.env[transfer_details.get('res_model')].\
                browse(transfer_details.get('res_id'))
            if serial_number:
                if len(serial_number) == 1:
                    for transfer_item in wizard_for_transfer.item_ids:
                        transfer_item.lot_id = serial_number[0].id
                else:
                    # Case for the A, B & C serial numbers: That are 3 like
                    # value for the quantity field in the wizard, so we should
                    # split this record 2 times.
                    # Splitting the record and executing the transfer
                    wizard_split = wizard_for_transfer.item_ids[0].\
                        split_quantities()
                    wizard_for_transfer = self.env['stock.transfer_details'].\
                        browse(wizard_split.get('res_id'))
                    wizard_split = wizard_for_transfer.item_ids[0].\
                        split_quantities()
                    wizard_for_transfer = self.env['stock.transfer_details'].\
                        browse(wizard_split.get('res_id'))
                    index = 0
                    for transfer_item in wizard_for_transfer.item_ids:
                        transfer_item.lot_id = serial_number[index].id
                        index += 1
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
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        stock_move_datas = [{
            'product_id': product.id,
            'qty': 1.0
        }]
        # Creating the pickings
        picking_data_1 = {
            'name': 'Test Picking IN 1',
        }
        picking_data_2 = {
            'name': 'Test Picking IN 2',
        }
        picking_1 = self.create_stock_picking(
            stock_move_datas, picking_data_1,
            self.env.ref('stock.picking_type_in'))
        picking_2 = self.create_stock_picking(
            stock_move_datas, picking_data_2,
            self.env.ref('stock.picking_type_in'))
        # Executing the wizard for pickings transfering
        self.transfer_picking(
            picking_1,
            self.env.ref('product_unique_serial.serial_number_demo_1'))
        with self.assertRaisesRegexp(
                except_orm,
                r"you will have a quantity of '2.0' "
                r"in lot '86137801852514'"):
            self.transfer_picking(
                picking_2,
                [self.env.ref('product_unique_serial.serial_number_demo_1')])

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
        NOTE: To can operate this case, we need an IN PICKING
        Warehouse: Your Company
        """
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        stock_move_datas = [{
            'product_id': product.id,
            'qty': 1.0
        }]
        # Creating the pickings
        picking_data_in = {
            'name': 'Test Picking IN 1',
        }
        picking_data_out_1 = {
            'name': 'Test Picking OUT 1',
        }
        picking_data_out_2 = {
            'name': 'Test Picking OUT 2',
        }
        # IN PROCESS
        picking_in = self.create_stock_picking(
            stock_move_datas, picking_data_in,
            self.env.ref('stock.picking_type_in'))
        self.transfer_picking(
            picking_in,
            self.env.ref('product_unique_serial.serial_number_demo_1'))
        # OUT PROCESS
        picking_out_1 = self.create_stock_picking(
            stock_move_datas, picking_data_out_1,
            self.env.ref('stock.picking_type_out'))
        picking_out_2 = self.create_stock_picking(
            stock_move_datas, picking_data_out_2,
            self.env.ref('stock.picking_type_out'))
        # Executing the wizard for pickings transfering
        self.transfer_picking(
            picking_out_1,
            self.env.ref('product_unique_serial.serial_number_demo_1'))
        with self.assertRaisesRegexp(
                except_orm,
                r"you will have a quantity of '-1.0' "
                r"in lot '86137801852514'"):
            self.transfer_picking(
                picking_out_2,
                [self.env.ref('product_unique_serial.serial_number_demo_1')])

    def test_3_1product_qtyno1_1serialnumber_1p_in(self):
        """
        Test 3. Creating a picking with 1 product for the same serial number,
        in the delivery orders scope, with the next form:
        - Picking 1
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||     >1     ||      001       ||
        =============================================
        Warehouse: Your Company
        """
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        stock_move_datas = [{
            'product_id': product.id,
            'qty': 2.0
        }]
        # Creating the pickings
        picking_data_1 = {
            'name': 'Test Picking IN 1',
        }
        picking_1 = self.create_stock_picking(
            stock_move_datas, picking_data_1,
            self.env.ref('stock.picking_type_in'))
        # Executing the wizard for pickings transfering
        with self.assertRaisesRegexp(except_orm, r'but has qty > 1'):
            self.transfer_picking(
                picking_1,
                [self.env.ref('product_unique_serial.serial_number_demo_2')])

    def test_4_1product_qty3_3serialnumber_1p_in(self):
        """
        Test 4. Creating a picking with 1 product for three serial numbers,
        in the receipts scope, with the next form:
        - Picking 1
        =============================================
        || Product ||  Quantity  ||  Serial Number ||
        =============================================
        ||    A    ||      1     ||      001       ||
        =============================================
        ||    A    ||      1     ||      002       ||
        =============================================
        ||    A    ||      1     ||      003       ||
        =============================================
        Warehouse: Your Company
        """
        test_passed = True
        # Creating move line for picking
        product = self.env.ref('product_unique_serial.product_demo_1')
        stock_move_datas = [
            {'product_id': product.id, 'qty': 1.0},
            {'product_id': product.id, 'qty': 1.0},
            {'product_id': product.id, 'qty': 1.0}
        ]
        # Creating the picking
        picking_data_in = {
            'name': 'Test Picking IN 1',
        }
        picking_in = self.create_stock_picking(
            stock_move_datas, picking_data_in,
            self.env.ref('stock.picking_type_in'))
        # Executing the wizard for pickings transfering
        try:
            self.transfer_picking(
                picking_in,
                [self.env.ref('product_unique_serial.serial_number_demo_1'),
                 self.env.ref('product_unique_serial.serial_number_demo_2'),
                 self.env.ref('product_unique_serial.serial_number_demo_3')]
            )
        except except_orm, msg:
            print msg
            test_passed = False
        self.assertTrue(
            test_passed,
            "ERROR: The module can't operate with a product that has many"
            "associated serial numbers, of course each one being unique ..."
            "This error should be fixed")

    def test_5_1product_1serialnumber_2p_internal(self):
        """
        Test 5. Creating 2 pickings with 1 product for the same serial number,
        in the internal scope, with the next form:
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
        NOTE: To can operate this case, we need an IN PICKING
        Warehouse: Your Company
        """
        product = self.env.ref('product_unique_serial.product_demo_2')
        stock_move_in_datas = [
            {'product_id': product.id,
             'qty': 1.0,
             'source_loc': self.env.ref('stock.stock_location_suppliers').id,
             'destination_loc': self.env.ref(
                 'stock.stock_location_components').id}]
        stock_move_internal_datas = [
            {'product_id': product.id,
             'qty': 1.0,
             'source_loc': self.env.ref('stock.stock_location_components').id,
             'destination_loc': self.env.ref('stock.stock_location_14').id}]
        picking_data_in = {
            'name': 'Test Picking IN 1',
        }
        picking_data_internal_1 = {
            'name': 'Test Picking INTERNAL 1',
        }
        picking_data_internal_2 = {
            'name': 'Test Picking INTERNAL 2',
        }
        # IN PROCESS
        picking_in = self.create_stock_picking(
            stock_move_in_datas, picking_data_in,
            self.env.ref('stock.picking_type_in'))
        self.transfer_picking(
            picking_in,
            [self.env.ref('product_unique_serial.serial_number_demo_1')])
        # INTERNAL PROCESS
        picking_internal_1 = self.create_stock_picking(
            stock_move_internal_datas, picking_data_internal_1,
            self.env.ref('stock.picking_type_internal'))
        picking_internal_2 = self.create_stock_picking(
            stock_move_internal_datas, picking_data_internal_2,
            self.env.ref('stock.picking_type_internal'))
        self.transfer_picking(
            picking_internal_1,
            [self.env.ref('product_unique_serial.serial_number_demo_1')])
        with self.assertRaisesRegexp(
                except_orm,
                r"Product 'Nokia 2630' has active 'check no negative'"):
            self.transfer_picking(
                picking_internal_2,
                [self.env.ref('product_unique_serial.serial_number_demo_1')])

    @mute_logger('openerp.sql_db')
    def test_6_1serialnumber_1product_2records(self):
        """
        Test 7. Creating 2 identical serial numbers
        """
        product_id = self.env.ref('product_unique_serial.product_demo_1')
        lot_data = {
            'name': '86137801852520',
            'ref': '86137801852520',
            'product_id': product_id.id
        }
        self.stock_production_lot_obj.create(lot_data)
        with self.assertRaisesRegexp(
                IntegrityError, r'"stock_production_lot_name_ref_uniq"'):
            self.stock_production_lot_obj.create(lot_data)

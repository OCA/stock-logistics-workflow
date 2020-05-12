# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestStockPickingDoneManual(common.TransactionCase):

    def setUp(self):
        super(TestStockPickingDoneManual, self).setUp()
        self.picking_model = self.env['stock.picking']
        self.move_model = self.env['stock.move']
        self.usr_model = self.env['res.users']
        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.stock_location_customers = self.env.ref(
            'stock.stock_location_customers')
        group_ids = [
            self.env.ref('stock.group_stock_manager').id,
            self.env.ref('sales_team.group_sale_manager').id,
        ]
        user_dict = {
            'name': 'User test',
            'login': 'tua@example.com',
            'password': 'base-test-passwd',
            'email': 'armande.hruser@example.com',
            'groups_id': [(6, 0, group_ids)],
        }
        self.user_test = self.usr_model.create(user_dict)
        prod_dict = {
            'name': 'test product 1',
            'type': 'product',
        }
        self.product_1 = self.env['product.product'].sudo(
            self.user_test).create(prod_dict)
        prod_dict = {
            'name': 'test product 2',
            'type': 'product',
        }
        self.product_2 = self.env['product.product'].sudo(
            self.user_test).create(prod_dict)
        picking_type = self.env.ref('stock.picking_type_out')
        picking_type.allow_stock_picking_move_done_manual = True
        picking_dict = {
            'partner_id': self.env.ref('base.res_partner_1').id,
            'location_id': self.stock_location_stock.id,
            'location_dest_id': self.stock_location_customers.id,
            'picking_type_id': picking_type.id,
        }
        self.stock_picking = self.picking_model.sudo(
            self.user_test).create(picking_dict)
        move_dict_1 = {
            'name': '/',
            'picking_id': self.stock_picking.id,
            'product_id': self.product_1.id,
            'product_uom_qty': 2.0,
            'product_uom': self.product_1.uom_id.id,
            'location_id': self.stock_location_stock.id,
            'location_dest_id': self.stock_location_customers.id,
        }
        move_dict_2 = {
            'name': '/',
            'picking_id': self.stock_picking.id,
            'product_id': self.product_2.id,
            'product_uom_qty': 2.0,
            'product_uom': self.product_2.uom_id.id,
            'location_id': self.stock_location_stock.id,
            'location_dest_id': self.stock_location_customers.id,
        }
        self.move_1 = self.move_model.create(move_dict_1)
        self.move_2 = self.move_model.create(move_dict_2)
        self._update_product_qty(
            self.product_1, self.stock_location_stock, 10.0)
        self._update_product_qty(
            self.product_2, self.stock_location_stock, 10.0)

    def _update_product_qty(self, product, location, quantity):
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': location.id,
            'product_id': product.id,
            'new_quantity': quantity,
        })
        product_qty.change_product_qty()
        return product_qty

    def test_complete_move_out_picking_1(self):
        self.stock_picking.action_confirm()
        self.stock_picking.action_assign()
        self.stock_picking.move_lines[0].move_line_ids[0].qty_done = 2.0
        self.stock_picking.move_lines[0].action_manual_done_from_picking()
        self.assertEqual(self.stock_picking.move_lines[0].state, 'done')
        self.assertEqual(self.stock_picking.state, 'assigned')
        self.stock_picking.move_lines[1].move_line_ids[0].qty_done = 2.0
        self.stock_picking.move_lines[1].move_line_ids[0].\
            action_move_manual_done_from_picking()
        self.assertEqual(self.stock_picking.move_lines[0].state, 'done')
        self.assertEqual(self.stock_picking.state, 'done')

    def test_complete_move_out_picking_2(self):
        self.stock_picking.action_confirm()
        self.stock_picking.action_assign()
        immediate_transfer_wizard = self.stock_picking.button_validate()
        self.assertEqual(immediate_transfer_wizard['res_model'],
                         'stock.immediate.transfer')

    def test_partial_move_out_picking_1(self):
        self.stock_picking.action_confirm()
        self.stock_picking.action_assign()
        move_1 = self.stock_picking.move_lines.filtered(
            lambda m: m.product_id == self.product_1)
        move_1.move_line_ids[0].qty_done = 1.0
        move_1.action_manual_done_from_picking()
        self.assertEqual(move_1.state, 'done')
        self.assertEqual(self.stock_picking.state, 'assigned')
        move_1_1 = self.stock_picking.move_lines.filtered(
            lambda m: m.product_id == self.product_1 and m.state != 'done')
        self.assertEqual(move_1_1.state, 'assigned')
        move_1_1.move_line_ids[0].qty_done = 1.0
        move_1_1.action_manual_done_from_picking()
        self.assertEqual(move_1_1.state, 'done')
        self.assertEqual(self.stock_picking.state, 'assigned')
        move_2 = self.stock_picking.move_lines.filtered(
            lambda m: m.product_id == self.product_2)
        move_2.move_line_ids[0].qty_done = 2.0
        move_2.move_line_ids[0].action_move_manual_done_from_picking()
        self.assertEqual(move_2.state, 'done')
        self.assertEqual(self.stock_picking.state, 'done')

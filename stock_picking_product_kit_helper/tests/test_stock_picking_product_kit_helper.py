# Copyright 2019 Kitti U. - Ecosoft <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common, Form
from odoo.exceptions import ValidationError


class TestStockPickingProductKitHelper(common.TransactionCase):

    def setUp(self):
        super(TestStockPickingProductKitHelper, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.table_kit = self.env.ref('mrp.product_product_table_kit')

    def test_00_sale_product_kit_helper(self):
        """Test sale order with product kit, I expect,
        - Product is exploded on picking
        - Use helper, will assign quantity to stock.move correctly
        - After picking is done, do not allow to use helper
        """
        # Create sales order of 10 table kit
        order_form = Form(self.env['sale.order'])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line:
            line.product_id = self.table_kit
            line.product_uom_qty = 10
        order = order_form.save()
        order.action_confirm()
        # In the picking, product line is exploded.
        picking = order.mapped('picking_ids')
        self.assertEqual(len(picking), 1)
        stock_moves = picking.move_lines
        # 1 SO line exploded to 2 moves
        moves = [{'product': x.product_id.name, 'qty': x.product_uom_qty}
                 for x in stock_moves]
        self.assertEqual(moves,
                         [{'product': 'Wood Panel', 'qty': 10.0},
                          {'product': 'Bolt', 'qty': 40.0}])
        self.assertTrue(picking.has_product_kit)
        self.assertFalse(picking.product_kit_helper_ids)  # Not show yet
        picking.show_product_kit()
        self.assertEqual(len(picking.product_kit_helper_ids), 1)
        # Assign product set 4 qty and test that it apply to stock.move
        picking.product_kit_helper_ids[0].write({'product_uom_qty': 4.0})
        picking.action_product_kit_helper()
        moves = [{'product': x.product_id.name, 'qty': x.quantity_done}
                 for x in stock_moves]
        self.assertEqual(moves,
                         [{'product': 'Wood Panel', 'qty': 4.0},
                          {'product': 'Bolt', 'qty': 16.0}])
        # Assign again to 10 qty
        picking.product_kit_helper_ids[0].write({'product_uom_qty': 10.0})
        picking.action_product_kit_helper()
        moves = [{'product': x.product_id.name, 'qty': x.quantity_done}
                 for x in stock_moves]
        self.assertEqual(moves,
                         [{'product': 'Wood Panel', 'qty': 10.0},
                          {'product': 'Bolt', 'qty': 40.0}])
        # Validate Picking
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        # After done state, block the helper
        with self.assertRaises(ValidationError):
            picking.action_product_kit_helper()

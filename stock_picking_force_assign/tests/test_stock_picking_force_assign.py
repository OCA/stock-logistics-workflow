# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestStockPickingForceAssign(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        route_buy = self.env['stock.location.route'].create({
            'name': 'Buy',
            'rule_ids': [(0, 0, {
                'name': 'Buy',
                'action': 'buy',
                'picking_type_id': self.env.ref('stock.picking_type_in').id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
            })]
        })
        route_mto = self.env.ref('stock.route_warehouse0_mto')
        self.product = self.env['product.product'].create({
            'name': 'stockable',
            'type': 'product',
        })
        self.product2 = self.product.copy({
            'name': 'stockable-mto',
            'purchase_ok': True,
            'sale_ok': True,
            'route_ids': [(6, 0, [route_mto.id, route_buy.id])],
            'seller_ids': [(0, 0, {
                'name': self.env.ref('base.main_partner').id,
                'min_qty': 1,
                'product_name': 'stockable',
                'product_code': 'stockable',
            })],
        })
        self.assigned_picking = self.env['stock.picking'].create({
            'name': 'Picking to unassign',
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'product_uom_qty': 42,
            })],
        })
        self.env['stock.quant'].create({
            'location_id': self.assigned_picking.location_id.id,
            'product_id': self.product.id,
            'quantity': 42,
        })
        self.assigned_picking.action_assign()
        self.assertEqual(self.assigned_picking.state, 'assigned')
        self.waiting_picking = self.assigned_picking.copy({
            'name': 'Picking to assign',
        })
        self.waiting_picking.action_assign()
        self.assertEqual(self.waiting_picking.state, 'confirmed')
        self.waitanother_picking = self.env['stock.picking'].create({
            'name': 'Picking to unchain',
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
            'move_lines': [(0, 0, {
                'name': self.product2.name,
                'product_id': self.product2.id,
                'product_uom': self.product2.uom_id.id,
                'product_uom_qty': 12,
                'state': 'waiting',
                'procure_method': 'make_to_order',
            })],
        })
        self.env['stock.quant'].create({
            'location_id': self.waitanother_picking.location_id.id,
            'product_id': self.product2.id,
            'quantity': 12,
        })

    def test_happy_flow(self):
        """ Test unreservation works """
        self.waiting_picking.action_force_assign_pickings()
        self.assertEqual(self.waiting_picking.state, 'assigned')
        self.assertEqual(self.assigned_picking.state, 'confirmed')

    def test_errors(self):
        """ Test error cases """
        self.assigned_picking.move_line_ids.qty_done = 42
        self.assigned_picking.action_done()
        self.assertEqual(self.assigned_picking.state, 'done')
        with self.assertRaises(UserError):
            self.waiting_picking.action_force_assign_pickings()

    def test_waiting_another(self):
        """ Test unchaining moves waiting another operation """
        self.assertEqual(len(self.waitanother_picking), 1)
        self.assertEqual(self.waitanother_picking.state, 'waiting')
        self.assertEqual(
            self.waitanother_picking.move_lines[0].procure_method, 'make_to_order')
        self.waitanother_picking.action_force_assign_pickings()
        self.assertNotEqual(self.waitanother_picking.state, 'waiting')
        self.assertEqual(
            self.waitanother_picking.move_lines[0].procure_method, 'make_to_stock')

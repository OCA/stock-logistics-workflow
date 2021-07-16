# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestStockPickingForceAssign(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.product = self.env['product.product'].create({
            'name': 'stockable',
            'type': 'product',
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

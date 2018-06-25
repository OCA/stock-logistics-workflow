# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Camptocamp SA - Julien Coux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestStockSplitPicking(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockSplitPicking, cls).setUpClass()

        cls.src_location = cls.env.ref('stock.stock_location_stock')
        cls.dest_location = cls.env.ref('stock.stock_location_customers')
        cls.transit_location = cls.env.ref('stock.stock_location_inter_wh')
        cls.picking_type = cls.env.ref('stock.picking_type_out')
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })

        cls.picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.picking_type.id,
            'location_id': cls.src_location.id,
            'location_dest_id': cls.dest_location.id,
        })
        cls.move = cls.env['stock.move'].create({
            'name': '/',
            'picking_id': cls.picking.id,
            'product_id': cls.product.id,
            'product_uom_qty': 10,
            'product_uom': cls.product.uom_id.id,
            'location_id': cls.src_location.id,
            'location_dest_id': cls.dest_location.id,
        })

        cls.transit_picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.picking_type.id,
            'location_id': cls.src_location.id,
            'location_dest_id': cls.transit_location.id,
        })
        cls.transit_move = cls.env['stock.move'].create({
            'name': 'Transit',
            'picking_id': cls.transit_picking.id,
            'product_id': cls.product.id,
            'product_uom_qty': 10,
            'product_uom': cls.product.uom_id.id,
            'location_id': cls.src_location.id,
            'location_dest_id': cls.transit_location.id,
        })
        location_route = cls.env['stock.location.route'].create({
            'name': 'Unittest route',
        })
        cls.picking_type.warehouse_id.route_ids = location_route
        # Push rule triggering a move transit > customer
        cls.env['stock.location.path'].create({
            'name': 'Push rule for transit',
            'active': True,
            'location_from_id': cls.transit_location.id,
            'location_dest_id': cls.dest_location.id,
            'picking_type_id': cls.picking_type.id,
            'route_id': location_route.id,
        })

    def test_stock_split_picking(self):
        # Picking state is draft
        self.assertEqual(self.picking.state, 'draft')
        # We can't split a draft picking
        with self.assertRaises(UserError):
            self.picking.split_process()
        # Confirm picking
        self.picking.action_confirm()
        # We can't split an unassigned picking
        with self.assertRaises(UserError):
            self.picking.split_process()
        # We assign quantities in order to split
        self.picking.action_assign()
        move_line = self.env['stock.move.line'].search(
            [('picking_id', '=', self.picking.id)], limit=1)
        move_line.qty_done = 4
        # Split picking: 4 and 6
        self.picking.split_process()

        # We have a picking with 4 units in state assigned
        self.assertEqual(move_line.qty_done, 4)
        self.assertEqual(move_line.product_qty, 4)
        self.assertEqual(move_line.product_uom_qty, 4)
        self.assertEqual(move_line.ordered_qty, 10)

        self.assertEqual(self.move.quantity_done, 4)
        self.assertEqual(self.move.product_qty, 4)
        self.assertEqual(self.move.product_uom_qty, 4)
        self.assertEqual(self.move.ordered_qty, 10)

        self.assertEqual(self.picking.state, 'assigned')
        # An another one with 6 units in state assigned
        new_picking = self.env['stock.picking'].search(
            [('backorder_id', '=', self.picking.id)], limit=1)
        move_line = self.env['stock.move.line'].search(
            [('picking_id', '=', new_picking.id)], limit=1)

        self.assertEqual(move_line.qty_done, 0)
        self.assertEqual(move_line.product_qty, 6)
        self.assertEqual(move_line.product_uom_qty, 6)
        self.assertEqual(move_line.ordered_qty, 6)

        self.assertEqual(new_picking.move_lines.quantity_done, 0)
        self.assertEqual(new_picking.move_lines.product_qty, 6)
        self.assertEqual(new_picking.move_lines.product_uom_qty, 6)
        self.assertEqual(new_picking.move_lines.ordered_qty, 6)

        self.assertEqual(new_picking.state, 'assigned')

    def test_chained_moves_spliting(self):
        self.transit_picking.action_confirm()
        self.transit_picking.action_assign()

        # Check chained picking and move have been created
        chained_move = self.transit_move.move_dest_ids
        self.assertEqual(1, len(chained_move))
        chained_picking = chained_move.picking_id
        self.assertEqual(1, len(chained_picking))

        self.assertEqual(chained_move.location_id.id, self.transit_location.id)
        self.assertEqual(chained_move.location_dest_id.id,
                         self.dest_location.id)
        self.assertEqual(chained_move.product_qty,
                         self.transit_move.product_qty)

        move_line = self.env['stock.move.line'].search(
            [('picking_id', '=', self.transit_picking.id)], limit=1)
        move_line.qty_done = 4
        # Split picking: 4 and 6
        self.transit_picking.split_process()

        transit_backorder = self.env['stock.picking'].search([
            ('backorder_id', '=', self.transit_picking.id)
        ])
        self.assertEqual(1, len(transit_backorder))

        self.assertEqual(4, self.transit_picking.move_lines.product_qty)
        self.assertEqual(6, transit_backorder.move_lines.product_qty)

        # Check that a backorder is also created for the chained picking
        chained_backorder = self.env['stock.picking'].search([
            ('backorder_id', '=', chained_picking.id)
        ])
        self.assertEqual(1, len(chained_backorder))

        self.assertEqual(self.transit_picking.move_lines.product_qty,
                         chained_picking.move_lines.product_qty)
        self.assertEqual(transit_backorder.move_lines.product_qty,
                         chained_backorder.move_lines.product_qty)

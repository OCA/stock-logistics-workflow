# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestStockSplitPicking(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockSplitPicking, cls).setUpClass()

        cls.src_location = cls.env.ref('stock.stock_location_stock')
        cls.dest_location = cls.env.ref('stock.stock_location_customers')
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
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
        pack_opt = self.env['stock.pack.operation'].search(
            [('picking_id', '=', self.picking.id)], limit=1)
        pack_opt.qty_done = 4.0
        # Split picking: 4 and 6
        self.picking.split_process()
        # We have a picking with 4 units in state assigned
        self.assertAlmostEqual(pack_opt.qty_done, 4.0)
        self.assertAlmostEqual(pack_opt.product_qty, 4.0)
        self.assertEqual(self.picking.state, 'assigned')
        # An another one with 6 units in state assigned
        new_picking = self.env['stock.picking'].search(
            [('backorder_id', '=', self.picking.id)], limit=1)
        pack_opt = self.env['stock.pack.operation'].search(
            [('picking_id', '=', new_picking.id)], limit=1)
        self.assertAlmostEqual(pack_opt.qty_done, 0.0)
        self.assertAlmostEqual(pack_opt.product_qty, 6.0)
        self.assertEqual(new_picking.state, 'assigned')

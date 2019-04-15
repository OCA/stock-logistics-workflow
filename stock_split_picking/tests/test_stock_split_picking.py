# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockSplitPicking(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestStockSplitPicking, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.src_location = cls.env.ref('stock.stock_location_stock')
        cls.dest_location = cls.env.ref('stock.stock_location_customers')

    def create_data(
            self, product_type='consu', multi_uom=False, with_lots=False):
        self.product = self.env['product.product'].create({
            'name': 'Test product',
            'type': product_type,
        })
        self.lot = self.env['stock.production.lot'].browse()
        if product_type == 'product':
            if with_lots:
                self.lot = self.env['stock.production.lot'].create({
                    'product_id': self.product.id,
                })
            wiz = self.env['stock.change.product.qty'].create({
                'location_id': self.src_location.id,
                'product_id': self.product.id,
                'new_quantity': 10.0,
                'lot_id': self.lot.id,
            })
            wiz.change_product_qty()
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.src_location.id,
            'location_dest_id': self.dest_location.id,
        })
        self.move = self.env['stock.move'].create({
            'name': '/',
            'picking_id': self.picking.id,
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'product_uom': self.product.uom_id.id,
            'location_id': self.src_location.id,
            'location_dest_id': self.dest_location.id,
            'restrict_lot_id': self.lot.id,
        })
        if multi_uom:
            # Add a dozen of products
            self.move2 = self.env['stock.move'].create({
                'name': '/',
                'picking_id': self.picking.id,
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'product_uom': self.env.ref('product.product_uom_dozen').id,
                'location_id': self.src_location.id,
                'location_dest_id': self.dest_location.id,
            })

    def test_stock_split_picking_confirmed(self):
        self.create_data()  # doesn't matter if consumable or stockable
        # Picking state is draft
        self.assertEqual(self.picking.state, 'draft')
        # Confirm picking
        self.picking.action_confirm()
        # Split picking: 4 and 6
        action = self.picking.split_process()
        wiz = self.env['stock.picking.split'].browse(action['res_id'])
        wiz.line_ids.split_qty = 6  # 6 qty for the new picking
        new_picking_id = wiz.process()['res_id']
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        # We have a picking with 4 units in state confirmed
        self.assertEqual(self.picking.state, 'confirmed')
        self.assertAlmostEqual(self.move.product_qty, 4)
        # An another one with 6 units in state confirmed
        split_move = new_picking.move_lines[0]
        self.assertAlmostEqual(split_move.product_qty, 6.0)
        self.assertEqual(new_picking.state, 'confirmed')

    def test_stock_split_picking_consumable_assigned(self):
        self.create_data(product_type='consu')
        # Picking state is draft
        self.assertEqual(self.picking.state, 'draft')
        # Confirm and assign picking
        self.picking.action_confirm()
        self.picking.action_assign()
        # Split picking: 4 and 6
        action = self.picking.split_process()
        wiz = self.env['stock.picking.split'].browse(action['res_id'])
        wiz.line_ids[0].split_qty = 6  # 6 qty for the new picking
        new_picking_id = wiz.process()['res_id']
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        # We have a picking with 4 units in state assigned
        self.assertEqual(self.picking.state, 'assigned')
        pack_opt = self.env['stock.pack.operation'].search(
            [('picking_id', '=', self.picking.id)], limit=1)
        self.assertAlmostEqual(pack_opt.product_qty, 4)
        # An another one with 6 units in state assigned
        split_pack_opt = self.env['stock.pack.operation'].search(
            [('picking_id', '=', new_picking.id)], limit=1)
        self.assertAlmostEqual(split_pack_opt.qty_done, 0.0)
        self.assertAlmostEqual(split_pack_opt.product_qty, 6.0)
        self.assertEqual(new_picking.state, 'assigned')

    def test_stock_split_picking_stockable_assigned(self):
        self.create_data(product_type='product')
        # Picking state is draft
        self.assertEqual(self.picking.state, 'draft')
        # Confirm picking
        self.picking.action_confirm()
        # We assign quantities in order to split
        self.picking.action_assign()
        # Split picking: 4 and 6
        action = self.picking.split_process()
        wiz = self.env['stock.picking.split'].browse(action['res_id'])
        wiz.line_ids[0].split_qty = 6
        new_picking_id = wiz.process()['res_id']
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        # We have a picking with 4 units in state assigned
        pack_opt = self.env['stock.pack.operation'].search(
            [('picking_id', '=', self.picking.id)], limit=1)
        self.assertAlmostEqual(pack_opt.qty_done, 0.0)
        self.assertAlmostEqual(pack_opt.product_qty, 4.0)
        self.assertEqual(self.picking.state, 'assigned')
        # An another one with 6 units in state assigned
        pack_opt = self.env['stock.pack.operation'].search(
            [('picking_id', '=', new_picking.id)], limit=1)
        self.assertAlmostEqual(pack_opt.qty_done, 0.0)
        self.assertAlmostEqual(pack_opt.product_qty, 6.0)
        self.assertEqual(new_picking.state, 'assigned')

    def test_stock_split_picking_confirmed_multi_uom(self):
        self.create_data(multi_uom=True)    # Unit + Dozen UoMs (two moves)
        uom_unit = self.env.ref('product.product_uom_unit')
        uom_dozen = self.env.ref('product.product_uom_dozen')
        # Picking state is draft
        self.assertEqual(self.picking.state, 'draft')
        # Confirm picking
        self.picking.action_confirm()
        # Split picking: 4 and 6
        action = self.picking.split_process()
        wiz = self.env['stock.picking.split'].browse(action['res_id'])
        wiz.line_ids.filtered(  # Assign 6 qty to the new picking
            lambda l: l.product_uom_id == uom_unit).split_qty = 6
        wiz.line_ids.filtered(  # Assign the dozen to the new picking
            lambda l: l.product_uom_id == uom_dozen).split_qty = 1
        new_picking_id = wiz.process()['res_id']
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        # We have a picking with 4 units in state confirmed
        self.assertEqual(self.picking.state, 'confirmed')
        move_uom_unit = self.picking.move_lines.filtered(
            lambda m: m.product_uom == uom_unit)
        move_uom_dozen = self.picking.move_lines.filtered(
            lambda m: m.product_uom == uom_dozen)   # Empty recordset
        self.assertAlmostEqual(move_uom_unit.product_qty, 4)
        self.assertFalse(move_uom_dozen)
        self.assertNotEqual(self.move2.picking_id, self.picking)
        self.assertAlmostEqual(self.move2.product_qty, 12)
        # An another one with 6 units in state confirmed
        split_move_uom_unit = new_picking.move_lines.filtered(
            lambda m: m.product_uom == uom_unit)
        split_move_uom_dozen = new_picking.move_lines.filtered(
            lambda m: m.product_uom == uom_dozen)
        self.assertAlmostEqual(split_move_uom_unit.product_qty, 6.0)
        self.assertAlmostEqual(split_move_uom_dozen.product_qty, 12.0)
        self.assertAlmostEqual(split_move_uom_dozen.product_uom_qty, 1.0)
        self.assertEqual(new_picking.state, 'confirmed')

    def test_stock_split_picking_confirmed_with_lots(self):
        self.create_data(product_type='product', with_lots=True)
        # Picking state is draft
        self.assertEqual(self.picking.state, 'draft')
        # Confirm picking
        self.picking.action_confirm()
        # Split picking: 4 and 6
        action = self.picking.split_process()
        wiz = self.env['stock.picking.split'].browse(action['res_id'])
        self.assertEqual(wiz.line_ids[0].restrict_lot_id, self.lot)
        wiz.line_ids[0].split_qty = 6  # 6 qty for the new picking
        new_picking_id = wiz.process()['res_id']
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        # We have a picking with 4 units in state confirmed
        self.assertEqual(self.picking.state, 'confirmed')
        self.assertAlmostEqual(self.move.product_qty, 4)
        # An another one with 6 units in state confirmed
        split_move = new_picking.move_lines[0]
        self.assertAlmostEqual(split_move.product_qty, 6.0)
        self.assertEqual(split_move.restrict_lot_id, self.lot)
        self.assertEqual(new_picking.state, 'confirmed')

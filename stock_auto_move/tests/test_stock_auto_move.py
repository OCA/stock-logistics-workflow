# -*- coding: utf-8 -*-
# Copyright 2014 NDP Systèmes (<http://www.ndp-systemes.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockAutoMove(common.TransactionCase):

    def setUp(self):
        super(TestStockAutoMove, self).setUp()
        self.product_a1232 = self.browse_ref("product.product_product_6")
        self.location_shelf = self.browse_ref(
            "stock.stock_location_components")
        self.location_1 = self.browse_ref("stock_auto_move.stock_location_a")
        self.location_2 = self.browse_ref("stock_auto_move.stock_location_b")
        self.location_3 = self.browse_ref("stock_auto_move.stock_location_c")
        self.product_uom_unit_id = self.ref("product.product_uom_unit")
        self.picking_type_id = self.ref("stock.picking_type_internal")
        self.auto_group_id = self.ref("stock_auto_move.automatic_group")

    def test_10_auto_move(self):
        """Check automatic processing of move with auto_move set."""
        move = self.env["stock.move"].create({
            'name': "Test Auto",
            'product_id': self.product_a1232.id,
            'product_uom': self.product_uom_unit_id,
            'product_uom_qty': 12,
            'location_id': self.location_1.id,
            'location_dest_id': self.location_2.id,
            'picking_type_id': self.picking_type_id,
            'auto_move': True,
        })
        move1 = self.env["stock.move"].create({
            'name': "Test Auto 2",
            'product_id': self.product_a1232.id,
            'product_uom': self.product_uom_unit_id,
            'product_uom_qty': 9,
            'location_id': self.location_1.id,
            'location_dest_id': self.location_2.id,
            'picking_type_id': self.picking_type_id,
            'auto_move': True,
        })
        move2 = self.env["stock.move"].create({
            'name': "Test Manual",
            'product_id': self.product_a1232.id,
            'product_uom': self.product_uom_unit_id,
            'product_uom_qty': 3,
            'location_id': self.location_1.id,
            'location_dest_id': self.location_2.id,
            'picking_type_id': self.picking_type_id,
            'auto_move': False,
        })
        move.action_confirm()
        self.assertTrue(move.picking_id)
        self.assertEqual(move.group_id.id, self.auto_group_id)
        move1.action_confirm()
        self.assertTrue(move1.picking_id)
        self.assertEqual(move1.group_id.id, self.auto_group_id)
        move2.action_confirm()
        self.assertTrue(move2.picking_id)
        self.assertFalse(move2.group_id)
        self.assertEqual(move.state, 'confirmed')
        self.assertEqual(move1.state, 'confirmed')
        self.assertEqual(move2.state, 'confirmed')
        move3 = self.env["stock.move"].create({
            'name': "Supply source location for test",
            'product_id': self.product_a1232.id,
            'product_uom': self.product_uom_unit_id,
            'product_uom_qty': 25,
            'location_id': self.location_shelf.id,
            'location_dest_id': self.location_1.id,
            'auto_move': False,
        })
        move3.action_confirm()
        move3.action_done()
        move.action_assign()
        move1.action_assign()
        move2.action_assign()
        self.assertEqual(move3.state, 'done')
        self.assertEqual(move2.state, 'assigned')
        self.assertEqual(move.state, 'done')
        self.assertEqual(move1.state, 'done')

    def test_20_procurement_auto_move(self):
        """Check that move generated with procurement rule
           have auto_move set."""
        self.product_a1232.route_ids = [
            (4, self.ref("stock_auto_move.test_route"))]
        proc = self.env["procurement.order"].create({
            'name': 'Test Procurement with auto_move',
            'date_planned': '2015-02-02 00:00:00',
            'product_id': self.product_a1232.id,
            'product_qty': 1,
            'product_uom': self.product_uom_unit_id,
            'warehouse_id': self.ref('stock.warehouse0'),
            'location_id': self.location_2.id,
        })
        proc.check()
        proc.run()
        self.assertEqual(
            proc.rule_id.id,
            self.ref("stock_auto_move.procurement_rule_a_to_b"))

        for move in proc.move_ids:
            self.assertEqual(move.auto_move, True)
            self.assertEqual(move.state, 'confirmed')

    def test_30_push_rule_auto(self):
        """Checks that push rule with auto set leads to an auto_move."""
        self.product_a1232.route_ids = [
            (4, self.ref("stock_auto_move.test_route"))]
        move3 = self.env["stock.move"].create({
            'name': "Supply source location for test",
            'product_id': self.product_a1232.id,
            'product_uom': self.product_uom_unit_id,
            'product_uom_qty': 7,
            'location_id': self.location_shelf.id,
            'location_dest_id': self.location_3.id,
            'auto_move': False,
        })
        move3.action_confirm()
        move3.action_done()
        quants_in_3 = self.env['stock.quant'].search(
            [('product_id', '=', self.product_a1232.id),
             ('location_id', '=', self.location_3.id)])
        quants_in_1 = self.env['stock.quant'].search(
            [('product_id', '=', self.product_a1232.id),
             ('location_id', '=', self.location_1.id)])
        self.assertEqual(len(quants_in_3), 0)
        self.assertGreater(len(quants_in_1), 0)

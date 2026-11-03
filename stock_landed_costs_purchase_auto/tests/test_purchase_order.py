# Copyright 2021-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import users

from .common import TestPurchaseOrderBase


class TestPurchaseOrder(TestPurchaseOrderBase):
    @users("test_purchase_user")
    def test_order_purchase_basic_user(self):
        self.order = self.order.with_user(self.env.user)
        self.order.button_confirm()
        self.assertTrue(self.order.landed_cost_ids)

    def test_order_lc(self):
        self.order.button_confirm()
        self.assertTrue(self.order.landed_cost_ids)
        picking = self.order.picking_ids
        self._action_picking_validate(picking)
        self.assertIn(picking, self.order.mapped("landed_cost_ids.picking_ids"))

    def test_order_lc_multi(self):
        self.order.order_line.product_qty = 2
        self.order.button_confirm()
        self.assertEqual(len(self.order.landed_cost_ids), 1)
        lc = self.order.landed_cost_ids
        picking = self.order.picking_ids
        self.assertIn(picking, lc.picking_ids)
        for move in picking.move_ids:
            move.quantity = 1
        self._action_picking_validate(picking)
        self.assertEqual(len(self.order.landed_cost_ids), 2)
        new_picking = self.order.picking_ids - picking
        self._action_picking_validate(new_picking)
        extra_lc = self.order.landed_cost_ids - lc
        self.assertNotIn(new_picking, lc.picking_ids)
        self.assertIn(new_picking, extra_lc.picking_ids)

    def test_order_lc_skips_dropship_picking(self):
        self.order.button_confirm()
        existing = self.order.landed_cost_ids
        dropship = self._create_dropship_picking()
        self.assertFalse(self.order._landed_cost_picking_eligible(dropship))
        self.assertFalse(self.order._create_picking_with_stock_landed_cost(dropship))
        self.assertEqual(self.order.landed_cost_ids, existing)

    def test_create_returns_the_landed_cost(self):
        self.order.button_confirm()
        picking = self.order.picking_ids
        self.assertTrue(self.order._landed_cost_picking_eligible(picking))
        landed_cost = self.order._create_picking_with_stock_landed_cost(picking)
        self.assertIn(landed_cost, self.order.landed_cost_ids)

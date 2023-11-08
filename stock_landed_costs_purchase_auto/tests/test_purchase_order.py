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
        for move in picking.move_ids_without_package:
            move.quantity_done = 1
        self._action_picking_validate(picking)
        self.assertEqual(len(self.order.landed_cost_ids), 2)
        new_picking = self.order.picking_ids - picking
        self._action_picking_validate(new_picking)
        extra_lc = self.order.landed_cost_ids - lc
        self.assertNotIn(new_picking, lc.picking_ids)
        self.assertIn(new_picking, extra_lc.picking_ids)

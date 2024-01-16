# Copyright 2021-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import users

from odoo.addons.stock_landed_costs_purchase_auto.tests.common import (
    TestPurchaseOrderBase,
)


class TestPurchaseOrder(TestPurchaseOrderBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_stock_landed_costs_delivery=True,
            )
        )
        product_carrier = cls.env["product.product"].create(
            {"name": "Carrier", "type": "service", "categ_id": cls.category.id}
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "product_id": product_carrier.id,
                "fixed_price": 10,
            }
        )
        cls.order.carrier_id = cls.carrier
        cls.purchase_user.write(
            {"groups_id": [(4, cls.env.ref("stock.group_stock_user").id)]}
        )

    @users("test_purchase_user")
    def test_order_with_lc_basic_user(self):
        self.order = self.order.with_user(self.env.user)
        self.order.button_confirm()
        lc = self.order.landed_cost_ids
        self.assertTrue(lc.state, "draft")
        picking = self.order.picking_ids
        self._action_picking_validate(picking)
        self.assertTrue(lc.state, "done")

    def test_order_with_lc_carrier_id(self):
        self.order.button_confirm()
        picking = self.order.picking_ids
        lc = self.order.landed_cost_ids
        self.assertEqual(len(lc.cost_lines), 0)
        self.assertEqual(lc.state, "draft")
        self._action_picking_validate(picking)
        self.assertEqual(len(lc.cost_lines), 1)
        self.assertEqual(lc.state, "done")
        self.assertIn(self.carrier.product_id, lc.cost_lines.mapped("product_id"))
        lc_cost_line = lc.cost_lines.filtered(
            lambda x: x.product_id == self.carrier.product_id
        )
        self.assertEqual(lc_cost_line.price_unit, 10)
        self.assertEqual(
            lc_cost_line.split_method, self.carrier.split_method_landed_cost_line
        )

    def test_order_with_lc_carrier_id_multi_01(self):
        """Order > Carrier. Picking 1 > Carrier. Picking 2 > Carrier."""
        self.order.order_line.product_qty = 2
        self.order.button_confirm()
        picking = self.order.picking_ids
        self.assertEqual(len(self.order.landed_cost_ids), 1)
        lc = self.order.landed_cost_ids
        self.assertEqual(len(lc.cost_lines), 0)
        self.assertEqual(lc.state, "draft")
        for move in picking.move_ids_without_package:
            move.quantity_done = 1
        self._action_picking_validate(picking)
        self.assertEqual(len(self.order.landed_cost_ids), 2)
        extra_lc = self.order.landed_cost_ids - lc
        self.assertEqual(len(lc.cost_lines), 1)
        self.assertEqual(lc.state, "done")
        self.assertEqual(extra_lc.state, "draft")
        self.assertEqual(lc.cost_lines.price_unit, 10)
        new_picking = self.order.picking_ids - picking
        self._action_picking_validate(new_picking)
        self.assertEqual(len(extra_lc.cost_lines), 1)
        self.assertEqual(extra_lc.state, "done")
        self.assertEqual(self.carrier.product_id, extra_lc.cost_lines.product_id)
        self.assertEqual(extra_lc.cost_lines.price_unit, 10)
        self.assertEqual(
            self.carrier.split_method_landed_cost_line,
            extra_lc.cost_lines.split_method,
        )

    def test_order_with_lc_carrier_id_multi_02(self):
        """Order > No Carrier. Picking 1 > No Carrier. Picking 2 > Carrier."""
        self.order.carrier_id = False
        self.order.order_line.product_qty = 2
        self.order.button_confirm()
        picking = self.order.picking_ids
        self.assertEqual(len(self.order.landed_cost_ids), 1)
        lc = self.order.landed_cost_ids
        self.assertEqual(len(lc.cost_lines), 0)
        self.assertEqual(lc.state, "draft")
        for move in picking.move_ids_without_package:
            move.quantity_done = 1
        self._action_picking_validate(picking)
        # Picking without carrier and LC without cost lines and draft state
        self.assertFalse(picking.carrier_id)
        self.assertEqual(len(self.order.landed_cost_ids), 2)
        extra_lc = self.order.landed_cost_ids - lc
        self.assertEqual(len(lc.cost_lines), 0)
        self.assertEqual(lc.state, "draft")
        self.assertEqual(extra_lc.state, "draft")
        new_picking = self.order.picking_ids - picking
        new_picking.carrier_id = self.carrier
        self._action_picking_validate(new_picking)
        # Order with carrier, delivery price and delivery line
        self.assertEqual(self.order.carrier_id, self.carrier)
        self.assertEqual(self.order.delivery_price, 10)
        self.assertEqual(
            len(self.order.order_line.filtered(lambda x: x.is_delivery)), 1
        )
        # LC keep draft state
        self.assertEqual(lc.state, "draft")
        # Extra LC done (cost line from delivery)
        self.assertEqual(len(extra_lc.cost_lines), 1)
        self.assertEqual(extra_lc.state, "done")
        self.assertEqual(self.carrier.product_id, extra_lc.cost_lines.product_id)
        self.assertEqual(extra_lc.cost_lines.price_unit, 10)
        self.assertEqual(
            self.carrier.split_method_landed_cost_line,
            extra_lc.cost_lines.split_method,
        )

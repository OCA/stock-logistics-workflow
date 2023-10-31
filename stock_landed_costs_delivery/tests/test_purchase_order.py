# Copyright 2021-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.stock_landed_costs_purchase_auto.tests.common import (
    TestPurchaseOrderBase,
)


class TestPurchaseOrder(TestPurchaseOrderBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_carrier = cls.env["product.product"].create(
            {"name": "Carrier", "type": "service"}
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "product_id": product_carrier.id,
                "fixed_price": 10,
            }
        )
        cls.order.carrier_id = cls.carrier

    def test_order_with_lc_carrier_id(self):
        self.order.button_confirm()
        picking = self.order.picking_ids
        lc = self.order.landed_cost_ids
        self.assertEqual(len(lc.cost_lines), 0)
        self._action_picking_validate(picking)
        self.assertEqual(len(lc.cost_lines), 1)
        self.assertIn(self.carrier.product_id, lc.cost_lines.mapped("product_id"))
        lc_cost_line = lc.cost_lines.filtered(
            lambda x: x.product_id == self.carrier.product_id
        )
        self.assertEqual(lc_cost_line.price_unit, 10)
        self.assertEqual(
            lc_cost_line.split_method, self.carrier.split_method_landed_cost_line
        )

    def test_order_with_lc_carrier_id_multi(self):
        self.order.order_line.product_qty = 2
        self.order.button_confirm()
        picking = self.order.picking_ids
        lc = self.order.landed_cost_ids
        self.assertEqual(len(lc.cost_lines), 0)
        for move in picking.move_ids_without_package:
            move.quantity_done = 1
        self._action_picking_validate(picking)
        self.assertEqual(len(lc.cost_lines), 1)
        lc_cost_lines = lc.cost_lines.filtered(
            lambda x: x.product_id == self.carrier.product_id
        )
        self.assertEqual(sum(lc_cost_lines.mapped("price_unit")), 10)
        new_picking = self.order.picking_ids - picking
        self._action_picking_validate(new_picking)
        self.assertEqual(len(lc.cost_lines), 2)
        self.assertIn(self.carrier.product_id, lc.cost_lines.mapped("product_id"))
        lc_cost_lines = lc.cost_lines.filtered(
            lambda x: x.product_id == self.carrier.product_id
        )
        self.assertEqual(sum(lc_cost_lines.mapped("price_unit")), 20)
        self.assertIn(
            self.carrier.split_method_landed_cost_line,
            lc_cost_lines.mapped("split_method"),
        )

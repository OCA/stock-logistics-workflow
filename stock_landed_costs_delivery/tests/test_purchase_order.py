# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.stock_landed_costs_purchase_auto.tests import test_purchase_order


class TestPurchaseOrder(test_purchase_order.TestPurchaseOrder):
    def setUp(self):
        super().setUp()
        product_carrier = self.env["product.product"].create(
            {"name": "Carrier", "type": "service"}
        )
        self.carrier = self.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "product_id": product_carrier.id,
                "fixed_price": 10,
            }
        )

    def test_order_with_lc_carrier_id(self):
        order = self._create_purchase_order()
        order.carrier_id = self.carrier
        order.button_confirm()
        lc = order.landed_cost_ids[0]
        self.assertTrue(self.carrier.product_id in lc.cost_lines.mapped("product_id"))
        lc_cost_line = lc.cost_lines.filtered(
            lambda x: x.product_id == self.carrier.product_id
        )
        self.assertEqual(lc_cost_line.price_unit, 10)
        self.assertEqual(
            lc_cost_line.split_method, self.carrier.split_method_landed_cost_line
        )

from .common import TestPurchaseStockLandedCostEstimateBase


class TestPurchaseStockLandedCostEstimate(TestPurchaseStockLandedCostEstimateBase):
    def test_cost_lines_calculation(self):
        self.order.button_confirm()
        landed_costs = self.order.landed_cost_ids
        # only one cost lines and the cost lines are 10% of the purchase price
        self.assertEqual(len(landed_costs.cost_lines), 1)
        self.assertEqual(landed_costs.cost_lines.price_unit, 1)
        # the state is draft unless the pickign is validated
        self.assertEqual(landed_costs.state, "draft")
        self._action_picking_validate(self.order.picking_ids)
        self.assertEqual(landed_costs.state, "done")
        # the stock move cost is the total
        self.assertEqual(
            self.order.picking_ids.move_ids.value,
            landed_costs.cost_lines.price_unit
            + self.order.order_line[0].price_subtotal,
        )

    def test_cost_lines_cancelation(self):
        self.order.button_confirm()
        self.order.picking_ids.action_cancel()
        landed_costs = self.order.landed_cost_ids
        self.assertEqual(landed_costs.state, "cancel")

    def test_no_cost_lines_when_no_supplierinfo(self):
        supplier2 = self.env["res.partner"].create({"name": "Supplier 2"})
        self.order.partner_id = supplier2
        self.order.button_confirm()
        landed_costs = self.order.landed_cost_ids
        self.assertEqual(len(landed_costs.cost_lines), 0)

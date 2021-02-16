# Copyright 2021 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestGroupByBase


class TestReport(TestGroupByBase):
    def _set_qty_only_in_location(self, location, product, qty):
        for other_location in self.env["stock.location"].search(
            [("usage", "!=", "view"), ("id", "!=", location.id)]
        ):
            self._update_qty_in_location(other_location, product, 0)
        self._update_qty_in_location(location, product, qty)
        self.assertEqual(product.qty_available, qty)

    def test_get_remaining_to_deliver_nondelivered_line(self):
        """One sale with two lines, one of them non delivered"""
        report = self.env["report.stock.report_deliveryslip"]

        stock_location = self.env.ref("stock.stock_location_stock")

        # SO1 has 5 units of product1, we have 3 in stock;
        # and has 7 units of product2, we have 0 in stock.
        so = self._get_new_sale_order(amount=5)
        prod1 = so.order_line[0].product_id
        self.assertEqual(prod1, self.env.ref("product.product_delivery_01"))
        prod2 = self.env.ref("product.product_delivery_02")
        self.env["sale.order.line"].create(
            {
                "order_id": so.id,
                "name": prod2.name,
                "product_id": prod2.id,
                "product_uom_qty": 7,
                "product_uom": prod2.uom_id.id,
                "price_unit": prod2.list_price,
            }
        )
        self._set_qty_only_in_location(stock_location, prod1, 3)
        self._set_qty_only_in_location(stock_location, prod2, 0)
        self.assertEqual(len(so.order_line), 2)
        so.action_confirm()

        self.assertEqual(len(so.picking_ids), 1)
        picking = so.picking_ids
        remaining_data = report.get_remaining_to_deliver(picking)
        self.assertEqual(len(remaining_data), 0)

        self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, picking.id)]}
        ).process()
        backorder_wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        backorder_wiz.process()

        remaining_data = report.get_remaining_to_deliver(picking)
        self.assertEqual(len(remaining_data), 3)

        self.assertTrue(remaining_data[0]["is_header"])
        self.assertEqual(remaining_data[0]["concept"], so.name)
        self.assertFalse(remaining_data[1]["is_header"])
        self.assertEqual(remaining_data[1]["qty"], 2)
        self.assertFalse(remaining_data[2]["is_header"])
        self.assertEqual(remaining_data[2]["qty"], 7)

    def test_get_remaining_to_deliver_two_sales(self):
        """Two sales that combine into one picking"""
        report = self.env["report.stock.report_deliveryslip"]

        stock_location = self.env.ref("stock.stock_location_stock")

        # SO1 has 5 units of product_delivery_01, we have 3 in stock,
        # so 5-3=2 will be pending.
        so1 = self._get_new_sale_order(amount=5)
        prod_so1 = so1.order_line[0].product_id
        self.assertEqual(prod_so1, self.env.ref("product.product_delivery_01"))
        self._set_qty_only_in_location(stock_location, prod_so1, 3)

        # SO2 has 10 units of product_delivery_02, we have 4 in stock,
        # so 10-4=6 will be pending.
        so2 = self._get_new_sale_order(amount=10)
        prod_so2 = self.env.ref("product.product_delivery_02")
        so2.order_line[0].update(
            {
                "name": prod_so2.name,
                "product_id": prod_so2.id,
                "product_uom": prod_so2.uom_id.id,
                "price_unit": prod_so2.list_price,
            }
        )
        self._set_qty_only_in_location(stock_location, prod_so2, 4)

        so1.action_confirm()
        so2.action_confirm()

        self.assertEqual(set(so1.picking_ids.ids), set(so2.picking_ids.ids))
        self.assertEqual(len(so1.picking_ids), 1)
        picking = so1.picking_ids
        self.assertEqual(len(picking.move_line_ids), 2)

        remaining_data = report.get_remaining_to_deliver(picking)
        self.assertEqual(len(remaining_data), 0)

        self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, picking.id)]}
        ).process()
        backorder_wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        backorder_wiz.process()
        remaining_data = report.get_remaining_to_deliver(picking)
        self.assertEqual(len(remaining_data), 4)

        self.assertTrue(remaining_data[0]["is_header"])
        self.assertEqual(remaining_data[0]["concept"], so1.name)
        self.assertFalse(remaining_data[1]["is_header"])
        self.assertEqual(remaining_data[1]["qty"], 2)
        self.assertTrue(remaining_data[2]["is_header"])
        self.assertEqual(remaining_data[2]["concept"], so2.name)
        self.assertFalse(remaining_data[3]["is_header"])
        self.assertEqual(remaining_data[3]["qty"], 6)

    def test_delivery_report_lines_two_sales_merged(self):
        """Check report lines for two sale orders merged in same picking."""
        so1 = self._get_new_sale_order()
        so2 = self._get_new_sale_order(amount=11)
        so1.action_confirm()
        so2.action_confirm()
        picking = so1.picking_ids
        res = picking.get_delivery_report_lines()
        self.assertEqual(len(res), 4)
        self.assertEqual(res._name, "stock.move")
        # Check that we have two display moves (sale name)
        # And two real moves.
        self.assertFalse(res[0].id)
        self.assertTrue(res[1].id)
        self.assertFalse(res[2].id)
        self.assertTrue(res[3].id)
        # Deliver and test again
        self._update_qty_in_location(
            picking.location_id,
            so1.order_line[0].product_id,
            so1.order_line[0].product_uom_qty,
        )
        self._update_qty_in_location(
            picking.location_id,
            so2.order_line[0].product_id,
            so2.order_line[0].product_uom_qty,
        )
        picking.action_assign()
        line = picking.move_lines[0].move_line_ids
        line.qty_done = line.product_uom_qty
        line = picking.move_lines[1].move_line_ids
        line.qty_done = line.product_uom_qty
        res = picking.action_done()
        self.assertEqual(picking.state, "done")
        res = picking.get_delivery_report_lines()
        self.assertEqual(len(res), 4)
        self.assertEqual(res._name, "stock.move.line")
        # Check that we have two display moves (sale name)
        # And two real moves.
        self.assertFalse(res[0].id)
        self.assertTrue(res[1].id)
        self.assertFalse(res[2].id)
        self.assertTrue(res[3].id)

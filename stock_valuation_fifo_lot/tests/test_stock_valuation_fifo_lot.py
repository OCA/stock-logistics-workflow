# Copyright 2024-2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.stock_valuation_fifo_lot.tests.common import (
    TestStockValuationFifoCommon,
)


class TestStockValuationFifoLot(TestStockValuationFifoCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_receive_deliver_return_deliver_lot(self):
        pick_in, move_in = self.create_picking(
            "in", ["001", "002", "003"], ml_qty=5.0, price=100.0
        )
        self.assertEqual(len(pick_in.move_line_ids), 3)
        self.assertEqual(move_in.stock_valuation_layer_ids.remaining_value, 1500.0)
        self.assertEqual(move_in.stock_valuation_layer_ids.remaining_qty, 15.0)
        pick_out, move_out = self.create_picking("out", ["002"])
        self.assertEqual(move_out.stock_valuation_layer_ids.value, -500.0)
        self.assertEqual(move_in.stock_valuation_layer_ids.remaining_qty, 10.0)
        ret_move_in = self.transfer_return(pick_out, 5.0)
        self.assertEqual(ret_move_in.stock_valuation_layer_ids.remaining_qty, 5.0)
        self.assertEqual(ret_move_in.stock_valuation_layer_ids.remaining_value, 500.0)
        _, move_out_2 = self.create_picking("out", ["002"])
        self.assertEqual(move_out_2.stock_valuation_layer_ids.value, -500.0)
        self.assertEqual(ret_move_in.stock_valuation_layer_ids.remaining_qty, 0.0)

    def test_delivery_use_incoming_price(self):
        self.create_picking("in", ["001"], ml_qty=5.0, price=100.0)
        self.create_picking("in", ["002"], ml_qty=5.0, price=200.0)
        pick_out, move_out = self.create_picking("out", ["002"], ml_qty=5.0)
        self.assertEqual(move_out.stock_valuation_layer_ids.value, -1000.0)
        ret_move_in = self.transfer_return(pick_out, 5.0)
        self.assertEqual(ret_move_in.stock_valuation_layer_ids.remaining_value, 1000.0)

    def test_change_qty_done_in_done_move_line(self):
        _, move_in = self.create_picking("in", ["001"], ml_qty=5.0, price=500.0)
        self.assertEqual(move_in.stock_valuation_layer_ids.remaining_value, 2500.0)
        ml_in = move_in.move_line_ids[0]
        with self.assertRaises(UserError):
            ml_in.qty_done += 1.0
        _, move_out = self.create_picking("out", ["001"], ml_qty=5.0)
        ml_out = move_out.move_line_ids[0]
        with self.assertRaises(UserError):
            ml_out.qty_done -= 1.0

    def test_inventory_adjustment_after_multiple_receipts(self):
        self.create_picking("in", ["001"], ml_qty=5.0, price=100.0)
        self.create_picking("in", ["002"], ml_qty=5.0, price=200.0)
        lot_002 = self.env["stock.lot"].search(
            [("name", "=", "002"), ("product_id", "=", self.product.id)], limit=1
        )
        quant_002 = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.stock_loc.id),
                ("product_id", "=", self.product.id),
                ("lot_id", "=", lot_002.id),
            ]
        )
        quant_002.inventory_quantity = 10.0
        quant_002.action_apply_inventory()
        move_adj = self.env["stock.move"].search(
            [("product_id", "=", self.product.id), ("is_inventory", "=", True)],
            limit=1,
        )
        self.assertEqual(move_adj.stock_valuation_layer_ids.value, 1000.0)

    def test_force_fifo_lot_id(self):
        _, move_in = self.create_picking("in", ["001", "002"], ml_qty=5.0, price=100.0)
        ml_in_001 = move_in.move_line_ids.filtered(lambda ml: ml.lot_name == "001")
        ml_in_002 = move_in.move_line_ids.filtered(lambda ml: ml.lot_name == "002")
        _, move_out_002 = self.create_picking("out", ["002"], ml_qty=5.0)
        self.assertEqual(move_out_002.stock_valuation_layer_ids.value, -500.0)
        # Intentioanally create inconsistent lot balances between stock.quant and
        # stock.move.line.
        # Move line qty_remaining is changed from 5.0 to 0.0 for lot 001
        ml_in_001.qty_consumed = 5.0
        self.assertEqual(ml_in_001.qty_remaining, 0.0)
        self.assertEqual(ml_in_001.value_remaining, 0.0)
        # Move line qty_remaining is changed from 0.0 to 5.0 for lot 001
        ml_in_002.qty_consumed = 0.0
        self.assertEqual(ml_in_002.qty_remaining, 5.0)
        self.assertEqual(ml_in_002.value_remaining, 500.0)
        # Create delivery for lot 001
        with self.assertRaises(UserError):
            self.create_picking("out", ["001"], ml_qty=5.0)
        _, move_out_001 = self.create_picking(
            "out", ["001"], ml_qty=5.0, force_lot_name="002"
        )
        self.assertEqual(move_out_001.stock_valuation_layer_ids.value, -500.0)

    def test_avco_product_receipt(self):
        self.product.categ_id.property_cost_method = "average"
        _, move_in = self.create_picking("in", ["001", "002"], ml_qty=5.0, price=100.0)
        self.assertFalse(move_in.stock_valuation_layer_ids.lot_ids)

    def test_fifo_revaluation_lot(self):
        pick_in, move_in = self.create_picking(
            "in", ["001", "002", "003"], ml_qty=5.0, price=100.0
        )
        self.assertEqual(len(pick_in.move_line_ids), 3)
        origin_layer = move_in.stock_valuation_layer_ids
        self.assertEqual(origin_layer.remaining_value, 1500.0)
        self.assertEqual(origin_layer.remaining_qty, 15.0)
        lot_001 = self.env["stock.lot"].search(
            [("product_id", "=", self.product.id), ("name", "=", "001")], limit=1
        )
        self.assertTrue(lot_001, "Lot 001 should exist")
        expense_account = self.env["account.account"].search(
            [("account_type", "=", "expense")], limit=1
        )
        revaluation = self.env["stock.valuation.layer.revaluation"].create(
            {
                "product_id": self.product.id,
                "company_id": self.env.company.id,
                "lot_id": lot_001.id,
                "added_value": 0.0,
                "reason": "Test Revaluation Lot 001",
                "account_id": expense_account.id,
            }
        )
        self.assertEqual(revaluation.new_value, 500.0)
        with self.assertRaises(UserError):
            revaluation.added_value = -550.0
            revaluation._compute_new_value()
        revaluation.added_value = -10.0
        self.assertEqual(revaluation.new_value, 490.0)
        revaluation.action_validate_revaluation()
        move_lines = self.env["stock.move.line"].search(
            [
                ("product_id", "=", self.product.id),
                ("lot_id", "=", lot_001.id),
                ("state", "=", "done"),
            ],
            order="id",
        )
        self.assertEqual(len(move_lines), 3, "There should be three move lines")
        # 1st move line is the original incoming move line
        self.assertEqual(move_lines[0].move_id, origin_layer.stock_move_id)
        self.assertEqual(move_lines[0].qty_remaining, 0.0)
        self.assertEqual(move_lines[0].value_remaining, 0.0)
        self.assertEqual(origin_layer.remaining_qty, 10.0)
        self.assertEqual(origin_layer.remaining_value, 1000.0)
        # 2nd move line is the revaluation "out" move line
        self.assertEqual(move_lines[1].location_id.usage, "internal")
        self.assertNotEqual(move_lines[1].location_dest_id.usage, "internal")
        self.assertEqual(move_lines[1].qty_done, 5.0)
        reval_out_layer = move_lines[1].move_id.stock_valuation_layer_ids
        self.assertEqual(reval_out_layer.quantity, -5.0)
        self.assertEqual(reval_out_layer.unit_cost, 100.0)
        self.assertEqual(reval_out_layer.value, -500.0)
        accounts = reval_out_layer.account_move_id.line_ids.mapped("account_id")
        self.assertIn(expense_account, accounts)
        # 3rd move line is the revaluation "in" move line
        self.assertNotEqual(move_lines[2].location_id.usage, "internal")
        self.assertEqual(move_lines[2].location_dest_id.usage, "internal")
        self.assertEqual(move_lines[2].qty_done, 5.0)
        self.assertEqual(move_lines[2].qty_remaining, 5.0)
        self.assertEqual(move_lines[2].value_remaining, 490.0)
        self.assertEqual(origin_layer.remaining_qty, 10.0)
        self.assertEqual(origin_layer.remaining_value, 1000.0)
        reval_in_layer = move_lines[2].move_id.stock_valuation_layer_ids
        self.assertEqual(reval_in_layer.quantity, 5.0)
        self.assertEqual(reval_in_layer.unit_cost, 98.0)
        self.assertEqual(reval_in_layer.value, 490.0)
        self.assertEqual(reval_in_layer.remaining_qty, 5.0)
        self.assertEqual(reval_in_layer.remaining_value, 490.0)
        accounts = reval_in_layer.account_move_id.line_ids.mapped("account_id")
        self.assertIn(expense_account, accounts)
        # Consume lot 001
        _, move_out = self.create_picking("out", ["001"], ml_qty=5.0)
        move_out_layer = move_out.stock_valuation_layer_ids
        self.assertEqual(move_out_layer.quantity, -5.0)
        self.assertEqual(move_out_layer.unit_cost, 98.0)
        self.assertEqual(move_out_layer.value, -490.0)
        self.assertEqual(reval_in_layer.remaining_qty, 0.0)
        self.assertEqual(reval_in_layer.remaining_value, 0.0)

# Copyright 2024 Quartile (https://www.quartile.co)
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
        receipt_picking, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001", "002", "003"],
            100.0,
        )
        self.assertEqual(len(receipt_picking.move_line_ids), 3)
        self.assertEqual(
            move_in.stock_valuation_layer_ids.remaining_value,
            1500.0,
            "Remaining value for receipt should be 1500.0",
        )
        self.assertEqual(
            move_in.stock_valuation_layer_ids.remaining_qty,
            15.0,
            "Remaining quantity for receipt should be 15.0",
        )

        delivery_picking, move_out = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["002"],
            is_receipt=False,
        )
        self.assertEqual(
            abs(move_out.stock_valuation_layer_ids.value),
            500.0,
            "Stock valuation for delivery of lot 002 should be 500.0",
        )
        self.assertEqual(
            move_in.stock_valuation_layer_ids.remaining_qty,
            10.0,
            "Remaining quantity for first incoming receipt should be 10.0",
        )

        return_move = self.transfer_return(delivery_picking, 5.0)
        self.assertEqual(
            return_move.stock_valuation_layer_ids.remaining_value,
            500.0,
            "Remaining value for returned lot 002 should be 500.0",
        )
        self.assertEqual(return_move.stock_valuation_layer_ids.remaining_qty, 5.0)

        _, move_out_2 = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["002"],
            is_receipt=False,
        )
        self.assertEqual(
            abs(move_out_2.stock_valuation_layer_ids.value),
            500.0,
            "Stock valuation for second delivery of lot 002 should be 500.0",
        )
        self.assertEqual(
            return_move.stock_valuation_layer_ids.remaining_qty,
            0.0,
            "The remaining qauntity of returned lot 002 should be 0.00",
        )

    def test_delivery_use_incoming_price(self):
        self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001"],
            100.0,
        )
        self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["002"],
            200.0,
        )
        delivery_picking, move_out = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["002"],
            is_receipt=False,
        )
        self.assertEqual(
            abs(move_out.stock_valuation_layer_ids.value),
            1000.0,
            "Stock valuation for delivery of lot 002 should be 1000.0",
        )

        return_move = self.transfer_return(delivery_picking, 5.0)
        self.assertEqual(
            return_move.stock_valuation_layer_ids.remaining_value,
            1000.0,
            "Remaining value for returned lot 002 should be 1000.0",
        )

    def test_change_qty_done_in_done_move_line(self):
        receipt_picking, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001"],
            500.0,
        )
        self.assertEqual(
            move_in.stock_valuation_layer_ids.remaining_value,
            2500.0,
            "Remaining value for the first receipt should be 2500.0",
        )

        move_line = receipt_picking.move_line_ids[0]
        move_line.qty_done += 2.0
        self.assertEqual(
            move_line.qty_done,
            7.0,
            "The qty_done of the incoming move line should be increased to 7.0",
        )
        self.assertEqual(
            sum(move_in.stock_valuation_layer_ids.mapped("value")),
            3500.0,
            "Stock valuation should reflect the increased qty_done",
        )

        move_line.qty_done -= 1.0
        self.assertEqual(
            move_line.qty_done,
            6.0,
            "The qty_done of the incoming move line should be decreased to 6.0",
        )
        self.assertEqual(
            sum(move_in.stock_valuation_layer_ids.mapped("value")),
            3000.0,
            "Stock valuation should reflect the decreased qty_done",
        )

        delivery_picking, move_out = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["001"],
            is_receipt=False,
        )
        self.assertEqual(
            abs(sum(move_out.stock_valuation_layer_ids.mapped("value"))),
            2500.0,
            "Stock valuation for the outgoing should be 2500.0",
        )

        move_line = delivery_picking.move_line_ids[0]
        move_line.qty_done -= 2.0
        self.assertEqual(
            move_line.qty_done,
            3.0,
            "The qty_done of the outgoing move line should be decreased to 3.0",
        )
        self.assertEqual(
            abs(sum(move_out.stock_valuation_layer_ids.mapped("value"))),
            1500.0,
            "Stock valuation should reflect the decreased qty_done",
        )

        move_line.qty_done += 1.0
        self.assertEqual(
            move_line.qty_done,
            4.0,
            "The qty_done of the outgoing move line should be increased to 4.0",
        )
        self.assertEqual(
            abs(sum(move_out.stock_valuation_layer_ids.mapped("value"))),
            2000.0,
            "Stock valuation should reflect the increased qty_done",
        )

    def test_inventory_adjustment_after_multiple_receipts(self):
        self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001"],
            100.0,
        )
        self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["002"],
            200.0,
        )
        lot = self.env["stock.lot"].search(
            [("name", "=", "002"), ("product_id", "=", self.product.id)], limit=1
        )
        inventory_quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.stock_location.id),
                ("product_id", "=", self.product.id),
                ("lot_id", "=", lot.id),
            ]
        )
        inventory_quant.inventory_quantity = 10.0
        inventory_quant.action_apply_inventory()
        move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id), ("is_inventory", "=", True)],
            limit=1,
        )
        self.assertEqual(
            move.stock_valuation_layer_ids.value,
            1000.0,
            "Stock valuation for lot 002 should be 1000.0 for positive quantity 5.",
        )

    def test_force_fifo_lot_id(self):
        _, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001", "002"],
            100.0,
        )
        self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["002"],
            is_receipt=False,
        )
        move_line_lot_001 = move_in.move_line_ids.filtered(
            lambda ml: ml.lot_name == "001"
        )
        move_line_lot_001.qty_remaining = 0.0
        move_line_lot_001.qty_consumed = 5.0
        move_line_lot_002 = move_in.move_line_ids.filtered(
            lambda ml: ml.lot_name == "002"
        )
        move_line_lot_002.qty_remaining = 5.0
        move_line_lot_002.qty_consumed = 0.0

        # Create delivery for lot 001
        with self.assertRaises(UserError):
            _, _ = self.create_picking(
                self.stock_location,
                self.customer_location,
                self.picking_type_out,
                ["001"],
                is_receipt=False,
            )
        _, move_out_001 = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["001"],
            is_receipt=False,
            force_lot_name="002",
        )
        self.assertEqual(
            abs(move_out_001.stock_valuation_layer_ids.value),
            500.0,
            "Stock valuation for the delivery of lot 001 should be 500.0",
        )

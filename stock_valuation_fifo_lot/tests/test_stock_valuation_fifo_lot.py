# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestStockValuationFifoLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_category = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": product_category.id,
                "tracking": "lot",
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def create_picking(
        self,
        location,
        location_dest,
        picking_type,
        lot_numbers,
        price_unit=0.0,
        is_receipt=True,
        force_lot_name=None,
    ):
        picking = self.env["stock.picking"].create(
            {
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "picking_type_id": picking_type.id,
            }
        )
        move_line_qty = 5.0
        move = self.env["stock.move"].create(
            {
                "name": "Test",
                "product_id": self.product.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": move_line_qty * len(lot_numbers),
                "picking_id": picking.id,
            }
        )
        if price_unit:
            move.write({"price_unit": price_unit})

        for lot in lot_numbers:
            move_line = self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": picking.id,
                    "product_id": self.product.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "product_uom_id": move.product_uom.id,
                    "qty_done": move_line_qty,
                }
            )
            if is_receipt:
                move_line.lot_name = lot
            else:
                lot = self.env["stock.lot"].search(
                    [("product_id", "=", self.product.id), ("name", "=", lot)], limit=1
                )
                move_line.lot_id = lot.id
                if force_lot_name:
                    force_lot = self.env["stock.lot"].search(
                        [
                            ("product_id", "=", self.product.id),
                            ("name", "=", force_lot_name),
                        ],
                        limit=1,
                    )
                    move_line.force_fifo_lot_id = force_lot.id
        picking.action_confirm()
        picking.action_assign()
        picking._action_done()
        return picking, move

    def transfer_return(self, original_picking, return_qty):
        """Handles product return for a given picking"""
        return_picking_wizard_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=original_picking.ids,
                active_id=original_picking.id,
                active_model="stock.picking",
            )
        )
        return_picking_wizard = return_picking_wizard_form.save()
        return_picking_wizard.product_return_moves.write({"quantity": return_qty})
        return_picking_wizard_action = return_picking_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(
            return_picking_wizard_action["res_id"]
        )
        return_move = return_picking.move_ids
        return_move.move_line_ids.qty_done = return_qty
        return_picking.button_validate()
        return return_move

    def test_stock_valuation_fifo_lot(self):
        _, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001"],
            100.0,
        )
        self.assertEqual(
            move_in.stock_valuation_layer_ids.value,
            500.0,
            "Stock valuation for the first receipt should be 500.0",
        )

        _, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["002"],
            200.0,
        )
        self.assertEqual(
            move_in.stock_valuation_layer_ids.value,
            1000.0,
            "Stock valuation for the second receipt should be 1000.0",
        )
        self.assertEqual(
            self.product.standard_price,
            100.0,
            "Standard price should be set to 100.0 after first receipt",
        )

        # Create delivery for lot 002
        _, move_out = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["002"],
            is_receipt=False,
        )
        self.assertEqual(
            abs(move_out.stock_valuation_layer_ids.value),
            1000.0,
            "Stock valuation for the delivery should be 1000.0",
        )

        # Test return receipt
        receipt_picking_3, move = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["003"],
            300.0,
        )
        self.assertEqual(
            move.stock_valuation_layer_ids.value,
            1500.0,
            "Stock valuation for the third receipt should be 1500.0",
        )

        return_move = self.transfer_return(receipt_picking_3, 5.0)
        self.assertEqual(
            abs(return_move.stock_valuation_layer_ids.value),
            1500.0,
            "Stock valuation after return should be 1500.0",
        )

    def test_receive_deliver_return_lot(self):
        receipt_picking, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001", "002", "003"],
            100.0,
        )
        self.assertEqual(len(receipt_picking.move_line_ids), 3)
        self.assertEqual(
            move_in.stock_valuation_layer_ids.value,
            1500.0,
            "Stock valuation for multiple receipts should be 1500.0",
        )
        self.assertEqual(move_in.stock_valuation_layer_ids.remaining_qty, 15.0)

        # Deliver lot 002
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
        self.assertEqual(move_in.stock_valuation_layer_ids.remaining_qty, 10.0)

        # Return lot 002
        move_in_2 = self.transfer_return(delivery_picking, 5.0)
        self.assertEqual(
            move_in_2.stock_valuation_layer_ids.value,
            500.0,
            "Stock valuation for returned lot 002 should be 500.0",
        )
        self.assertEqual(move_in_2.stock_valuation_layer_ids.remaining_qty, 5.0)

        # Deliver lot 002 again
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
        self.assertEqual(move_in_2.stock_valuation_layer_ids.remaining_qty, 0.0)

    def test_cost_tracking_by_lot(self):
        _, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001"],
            100.0,
        )
        self.assertEqual(
            move_in.stock_valuation_layer_ids.value,
            500.0,
            "Stock valuation for lot 001 should be 500.0",
        )

        _, move_in_2 = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["002"],
            200.0,
        )
        self.assertEqual(
            move_in_2.stock_valuation_layer_ids.value,
            1000.0,
            "Stock valuation for lot 002 should be 1000.0",
        )

        # Deliver lot 001
        self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["001"],
            is_receipt=False,
        )

        # Deliver lot 002
        delivery_picking_2, _ = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["002"],
            is_receipt=False,
        )

        # Return lot 002
        move_in = self.transfer_return(delivery_picking_2, 5.0)
        self.assertEqual(
            move_in.stock_valuation_layer_ids.value,
            1000.0,
            "Stock valuation for returned lot 002 should be 1000.0",
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
            move_in.stock_valuation_layer_ids.value,
            2500.0,
            "Stock valuation for the first receipt should be 2500.0",
        )
        # Change qty_done of the move line (increase)
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

        # Change qty_done of the move line (decrease)
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

        # Change qty_done of the move line (increase)
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

        # Change qty_done of the move line (decrease)
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
        _, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001"],
            100.0,
        )
        self.assertEqual(
            move_in.stock_valuation_layer_ids.value,
            500.0,
            "Stock valuation for lot 0001 should be 500.0",
        )

        _, move_in_2 = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["002"],
            200.0,
        )
        self.assertEqual(
            move_in_2.stock_valuation_layer_ids.value,
            1000.0,
            "Stock valuation for lot 0002 should be 1000.0",
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
            "Stock valuation for lot 002 should be 1000.0",
        )

    def test_force_fifo_lot_id(self):
        _, move_in = self.create_picking(
            self.supplier_location,
            self.stock_location,
            self.picking_type_in,
            ["001", "002"],
            100.0,
        )
        # Deliver lot 002
        _, move_out_002 = self.create_picking(
            self.stock_location,
            self.customer_location,
            self.picking_type_out,
            ["002"],
            is_receipt=False,
        )
        self.assertEqual(
            abs(move_out_002.stock_valuation_layer_ids.value),
            500.0,
            "Stock valuation for the delivery of lot 002 should be 500.0",
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

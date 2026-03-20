# Copyright (C) 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockMoveDisableExtra(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create products with lot tracking
        self.product_lot = self.env["product.product"].create(
            {
                "name": "Product with Lot",
                "type": "product",
                "tracking": "lot",
            }
        )

        # Create picking type with extra moves disabled
        self.picking_type = self.env["stock.picking.type"].create(
            {
                "name": "Test Receipt Type",
                "code": "incoming",
                "sequence_code": "TEST",
                "disable_extra_moves": True,
                "warehouse_id": self.env.ref("stock.warehouse0").id,
                "default_location_src_id": self.env.ref(
                    "stock.stock_location_suppliers"
                ).id,
                "default_location_dest_id": self.env.ref(
                    "stock.stock_location_stock"
                ).id,
            }
        )

        # Create a receipt
        self.picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )

        # Create move
        self.move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product_lot.id,
                "product_uom_qty": 10,
                "product_uom": self.product_lot.uom_id.id,
                "picking_id": self.picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )

        self.picking.action_confirm()
        self.picking.action_assign()

        # Create picking type with extra moves enabled (for normal behavior test)
        self.picking_type_normal = self.env["stock.picking.type"].create(
            {
                "name": "Test Receipt Type Normal",
                "code": "incoming",
                "sequence_code": "TESTN",
                "disable_extra_moves": False,  # Extra moves enabled
                "warehouse_id": self.env.ref("stock.warehouse0").id,
                "default_location_src_id": self.env.ref(
                    "stock.stock_location_suppliers"
                ).id,
                "default_location_dest_id": self.env.ref(
                    "stock.stock_location_stock"
                ).id,
            }
        )

    def test_extra_move_disabled_preserves_lot(self):
        """Test that when extra moves are disabled, lot information is preserved."""

        # Create a lot
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT001",
                "product_id": self.product_lot.id,
                "company_id": self.env.company.id,
            }
        )

        # Set quantity done to more than demand (15 instead of 10)
        self.move.move_line_ids.write(
            {
                "lot_id": lot.id,
                "quantity": 15,
            }
        )

        # Validate the picking
        self.picking.button_validate()

        # Check that no extra move was created
        self.assertEqual(
            len(self.picking.move_ids), 1, "Extra move should not be created"
        )

        # Check that the move quantity remains unchanged
        self.assertEqual(
            self.move.product_uom_qty, 10, "Move quantity should remain unchanged"
        )

        # Check that the move line still has the excess quantity
        self.assertEqual(
            self.move.move_line_ids.quantity,
            15,
            "Move line should have the excess quantity",
        )

        # Check that lot information is preserved
        self.assertEqual(
            self.move.move_line_ids.lot_id.id,
            lot.id,
            "Lot information should be preserved",
        )

        # Check that the quantity done is preserved
        self.assertEqual(self.move.quantity, 15, "Quantity done should be preserved")

        # Check that excess quantity is stored
        self.assertEqual(
            self.move.excess_quantity, 5, "Excess quantity should be stored"
        )

    def test_extra_move_enabled_normal_behavior(self):
        """Test that when extra moves are enabled (default), normal behavior occurs."""

        # Create a new receipt with the normal picking type (extra moves enabled)
        picking_normal = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_normal.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )

        # Create move for the normal picking
        move_normal = self.env["stock.move"].create(
            {
                "name": "Test Move Normal",
                "product_id": self.product_lot.id,
                "product_uom_qty": 10,
                "product_uom": self.product_lot.uom_id.id,
                "picking_id": picking_normal.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )

        picking_normal.action_confirm()
        picking_normal.action_assign()

        # Create a lot
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT002",
                "product_id": self.product_lot.id,
                "company_id": self.env.company.id,
            }
        )

        # Set quantity done to more than demand (15 instead of 10)
        move_normal.move_line_ids.write(
            {
                "lot_id": lot.id,
                "quantity": 15,
            }
        )

        # Validate the picking
        picking_normal.button_validate()

        # Check that an extra move was created
        self.assertEqual(
            len(picking_normal.move_ids),
            2,
            "Extra move should be created when feature is disabled",
        )

        # Check that the original move keeps its original quantity
        original_move = picking_normal.move_ids.filtered(lambda m: m == move_normal)
        self.assertEqual(
            original_move.product_uom_qty,
            10,
            "Original move should keep original quantity",
        )

        # Check that the extra move has the excess quantity
        extra_move = picking_normal.move_ids - original_move
        self.assertEqual(
            extra_move.product_uom_qty, 5, "Extra move should have the excess quantity"
        )

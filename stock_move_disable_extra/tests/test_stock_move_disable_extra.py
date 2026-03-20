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

    def _create_picking_and_move(self, picking_type, move_name="Test Move"):
        """Helper to create a picking and move for the given picking type."""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )

        move = self.env["stock.move"].create(
            {
                "name": move_name,
                "product_id": self.product_lot.id,
                "product_uom_qty": 10,
                "product_uom": self.product_lot.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )

        picking.action_confirm()
        picking.action_assign()

        return picking, move

    def _assert_lot_information_preserved(self, move, lot):
        """Helper to assert that lot information is preserved."""
        self.assertEqual(
            move.move_line_ids.lot_id.id,
            lot.id,
            "Lot information should be preserved",
        )

    def _assert_excess_quantity_stored(self, move, excess_qty):
        """Helper to assert that excess quantity is stored."""
        self.assertEqual(
            move.excess_quantity, excess_qty, "Excess quantity should be stored"
        )

    def _create_lot(self, name):
        """Helper to create a lot for the test product."""
        return self.env["stock.lot"].create(
            {
                "name": name,
                "product_id": self.product_lot.id,
                "company_id": self.env.company.id,
            }
        )

    def _set_move_line_quantity(self, move, lot, quantity):
        """Helper to set the quantity and lot on a move line."""
        move.move_line_ids.write(
            {
                "lot_id": lot.id,
                "quantity": quantity,
            }
        )

    def test_extra_move_disabled_preserves_lot(self):
        """Test that when extra moves are disabled, lot information is preserved."""

        # Arrange
        lot = self._create_lot("LOT001")
        self._set_move_line_quantity(self.move, lot, 15)

        # Act
        self.picking.button_validate()

        # Assert
        self.assertEqual(
            len(self.picking.move_ids), 1, "Extra move should not be created"
        )
        self.assertEqual(
            self.move.product_uom_qty, 10, "Move quantity should remain unchanged"
        )
        self._assert_lot_information_preserved(self.move, lot)
        self.assertEqual(self.move.quantity, 15, "Quantity done should be preserved")
        self._assert_excess_quantity_stored(self.move, 5)

    def test_extra_move_enabled_normal_behavior(self):
        """Test that when extra moves are enabled (default), normal behavior occurs."""

        # Arrange
        picking_normal, move_normal = self._create_picking_and_move(
            self.picking_type_normal, "Test Move Normal"
        )
        lot = self._create_lot("LOT002")
        self._set_move_line_quantity(move_normal, lot, 15)

        # Act
        picking_normal.button_validate()

        # Assert
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

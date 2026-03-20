# Copyright (C) 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockMoveDisableExtra(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_lot = cls.env["product.product"].create(
            {
                "name": "Product with Lot Tracking",
                "type": "product",
                "tracking": "lot",
            }
        )

        # Create picking type with extra moves disabled
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Receipt Type",
                "code": "incoming",
                "sequence_code": "TEST",
                "disable_extra_moves": True,
                "warehouse_id": cls.env.ref("stock.warehouse0").id,
                "default_location_src_id": cls.env.ref(
                    "stock.stock_location_suppliers"
                ).id,
                "default_location_dest_id": cls.env.ref(
                    "stock.stock_location_stock"
                ).id,
            }
        )

        # Create picking type with extra moves enabled (for normal behavior test)
        cls.picking_type_normal = cls.env["stock.picking.type"].create(
            {
                "name": "Test Receipt Type Normal",
                "code": "incoming",
                "sequence_code": "TESTN",
                "disable_extra_moves": False,  # Extra moves enabled
                "warehouse_id": cls.env.ref("stock.warehouse0").id,
                "default_location_src_id": cls.env.ref(
                    "stock.stock_location_suppliers"
                ).id,
                "default_location_dest_id": cls.env.ref(
                    "stock.stock_location_stock"
                ).id,
            }
        )

    def setUp(self):
        super().setUp()
        # Create picking and move for the disabled extra moves test
        self.picking, self.move = self._create_picking_and_move(
            self.picking_type, "Test Move"
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
        self.assertEqual(
            self.move.move_line_ids.lot_id.id,
            lot.id,
            "Lot information should be preserved",
        )
        self.assertEqual(self.move.quantity, 15, "Quantity done should be preserved")
        self.assertEqual(
            self.move.excess_quantity, 5, "Excess quantity should be stored"
        )

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

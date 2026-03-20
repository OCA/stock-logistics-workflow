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

        # Create normal picking type (extra moves enabled by default)
        cls.picking_type_normal = cls.env["stock.picking.type"].create(
            {
                "name": "Test Receipt Type Normal",
                "code": "incoming",
                "sequence_code": "TESTN",
                "disable_extra_moves": False,
                "warehouse_id": cls.env.ref("stock.warehouse0").id,
                "default_location_src_id": cls.env.ref(
                    "stock.stock_location_suppliers"
                ).id,
                "default_location_dest_id": cls.env.ref(
                    "stock.stock_location_stock"
                ).id,
            }
        )

        # Create picking type with extra moves disabled by copying the normal one
        cls.picking_type = cls.picking_type_normal.copy(
            {
                "name": "Test Receipt Type",
                "sequence_code": "TEST",
                "disable_extra_moves": True,
            }
        )

        # Create a test lot that can be reused
        cls.test_lot = cls.env["stock.lot"].create(
            {
                "name": "TESTLOT001",
                "product_id": cls.product_lot.id,
                "company_id": cls.env.company.id,
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

    def _create_picking_and_move(self, picking_type, move_name):
        """Helper to create a picking and move for the given picking type."""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
            }
        )

        move = self.env["stock.move"].create(
            {
                "name": move_name,
                "product_id": self.product_lot.id,
                "product_uom_qty": 10,
                "product_uom": self.product_lot.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
            }
        )

        picking.action_confirm()
        picking.action_assign()

        return picking, move

    def test_extra_move_disabled_preserves_lot(self):
        """Test that when extra moves are disabled, lot information is preserved."""

        # Arrange
        picking, move = self._create_picking_and_move(self.picking_type, "Test Move")
        self._set_move_line_quantity(move, self.test_lot, 15)

        # Act
        picking.button_validate()

        # Assert
        self.assertEqual(len(picking.move_ids), 1, "Extra move should not be created")
        self.assertEqual(
            move.product_uom_qty, 10, "Move quantity should remain unchanged"
        )
        self.assertEqual(
            move.move_line_ids.lot_id.id,
            self.test_lot.id,
            "Lot information should be preserved",
        )
        self.assertEqual(move.quantity, 15, "Quantity done should be preserved")
        self.assertEqual(move.excess_quantity, 5, "Excess quantity should be stored")

    def test_extra_move_enabled_normal_behavior(self):
        """Test that when extra moves are enabled (default), normal behavior occurs."""

        # Arrange
        picking_normal, move_normal = self._create_picking_and_move(
            self.picking_type_normal, "Test Move Normal"
        )
        self._set_move_line_quantity(move_normal, self.test_lot, 15)

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

# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.fields import Command
from odoo.tests import tagged

from .common import StockMovePositionCommon


@tagged("post_install", "-at_install")
class TestStockMovePosition(StockMovePositionCommon):
    def test_picking_numbering(self):
        """The renumber action numbers the moves of any transfer type."""
        out_picking = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        out_picking.action_renumber_lines_positions()
        self.assertEqual(out_picking.move_ids[0].position, "1")
        self.assertEqual(out_picking.move_ids[1].position, "2")
        in_picking = self._create_picking(
            self.in_type, [(self.product, 10), (self.product_2, 10)]
        )
        in_picking.action_renumber_lines_positions()
        self.assertEqual(in_picking.move_ids[0].position, "1")
        self.assertEqual(in_picking.move_ids[1].position, "2")

    def test_auto_renumber_on_create(self):
        """Moves are numbered when the transfer is created."""
        picking = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        self.assertEqual(picking.move_ids[0].position, "1")
        self.assertEqual(picking.move_ids[1].position, "2")

    def test_auto_renumber_on_write_add_line(self):
        """A move added through the transfer is numbered after the others."""
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        picking.write(
            {
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_2.uom_id.id,
                            "location_id": self.out_type.default_location_src_id.id,
                            "location_dest_id": self.out_dest.id,
                        }
                    )
                ]
            }
        )
        self.assertEqual(picking.move_ids[0].position, "1")
        self.assertEqual(picking.move_ids[1].position, "2")

    def test_auto_renumber_on_move_create_with_existing_picking(self):
        """A move created in an existing transfer is numbered."""
        # Mirrors purchase_stock's _create_or_update_picking(), which
        # creates the new stock.move with picking_id already set on an
        # existing, already-numbered picking.
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "product_id": self.product_2.id,
                "product_uom_qty": 10,
                "product_uom": self.product_2.uom_id.id,
                "location_id": self.out_type.default_location_src_id.id,
                "location_dest_id": self.out_type.default_location_dest_id.id,
            }
        )
        self.assertEqual(picking.move_ids[0].position, "1")
        self.assertEqual(picking.move_ids[1].position, "2")

    def test_auto_renumber_on_move_write_picking_id(self):
        """A move assigned to a transfer afterwards is numbered."""
        # Mirrors stock.move._assign_picking(), which creates the move
        # without a picking_id and assigns it afterwards via write().
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        new_move = self.env["stock.move"].create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 10,
                "product_uom": self.product_2.uom_id.id,
                "location_id": self.out_type.default_location_src_id.id,
                "location_dest_id": self.out_type.default_location_dest_id.id,
            }
        )
        self.assertFalse(new_move.position)
        new_move.write({"picking_id": picking.id})
        self.assertEqual(picking.move_ids[0].position, "1")
        self.assertEqual(picking.move_ids[1].position, "2")

    def test_done_picking_still_renumbers(self):
        """A done transfer can still be renumbered."""
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        picking.state = "done"
        picking.action_renumber_lines_positions()
        self.assertEqual(picking.move_ids.position, "1")

    def test_split_keeps_positions(self):
        """A split move keeps the position of the original move."""
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        picking.action_confirm()
        move = picking.move_ids
        self.assertEqual(move.position, "1")
        new_move = self.env["stock.move"].create(move._split(4))
        self.assertEqual(new_move.position, "1")

    def test_order_by_position_is_numeric(self):
        """Moves sorted by position follow the numbers, not the text.

        Scenario:
            1. Create a transfer with 10 lines (positions 1 to 10).
            2. Sort its moves by position.
        Expected:
            - Position 10 comes last, not right after 1.
        """
        picking = self._create_picking(self.out_type, [(self.product, 1)] * 10)
        moves = self.env["stock.move"].search(
            [("picking_id", "=", picking.id)], order="position"
        )
        self.assertEqual(moves.mapped("position")[-2:], ["9", "10"])
        moves = self.env["stock.move"].search(
            [("picking_id", "=", picking.id)], order="position desc"
        )
        self.assertEqual(moves.mapped("position")[:2], ["10", "9"])

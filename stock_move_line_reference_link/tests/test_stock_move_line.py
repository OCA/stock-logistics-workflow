# Copyright 2026 Ametras Intelligence
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockMoveLineReferenceLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product Reference Link", "type": "product"}
        )
        cls.location_src = cls.env.ref("stock.stock_location_stock")
        cls.location_dest = cls.env.ref("stock.stock_location_customers")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.location_src.id,
                "location_dest_id": cls.location_dest.id,
            }
        )
        move_vals = {
            "name": cls.product.name,
            "product_id": cls.product.id,
            "product_uom_qty": 1.0,
            "product_uom": cls.product.uom_id.id,
            "location_id": cls.location_src.id,
            "location_dest_id": cls.location_dest.id,
        }
        cls.move_with_picking = cls.env["stock.move"].create(
            dict(move_vals, picking_id=cls.picking.id)
        )
        cls.move_without_picking = cls.env["stock.move"].create(move_vals)

        move_line_vals = {
            "product_id": cls.product.id,
            "product_uom_id": cls.product.uom_id.id,
            "qty_done": 1.0,
            "location_id": cls.location_src.id,
            "location_dest_id": cls.location_dest.id,
        }
        cls.move_line_with_picking = cls.env["stock.move.line"].create(
            dict(move_line_vals, move_id=cls.move_with_picking.id)
        )
        cls.move_line_without_picking = cls.env["stock.move.line"].create(
            dict(move_line_vals, move_id=cls.move_without_picking.id)
        )

    def test_linked_reference_with_picking(self):
        self.assertEqual(
            self.move_line_with_picking.linked_reference,
            self.picking,
            "A move line whose move belongs to a picking must link to that " "picking.",
        )

    def test_linked_reference_without_picking(self):
        self.assertEqual(
            self.move_line_without_picking.linked_reference,
            self.move_without_picking,
            "A move line whose move has no picking must link to the move " "itself.",
        )

    def test_linked_reference_without_move(self):
        move_line = self.env["stock.move.line"].new({})
        move_line._compute_linked_reference()
        self.assertFalse(
            move_line.linked_reference,
            "A move line with no move must have no linked reference.",
        )

# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockMoveLineReferenceLink(TransactionCase):
    def test_linked_reference_picking_or_move(self):
        product = self.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
            }
        )

        location = self.env.ref("stock.stock_location_stock")
        location_dest = self.env.ref("stock.stock_location_customers")

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
            }
        )

        move = self.env["stock.move"].create(
            {
                "name": "Test move",
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
            }
        )

        move_line = self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "quantity": 1.0,
            }
        )

        # With picking
        self.assertEqual(move_line.linked_reference, picking)

        # Without picking
        move.picking_id = False
        self.assertEqual(move_line.linked_reference, move)

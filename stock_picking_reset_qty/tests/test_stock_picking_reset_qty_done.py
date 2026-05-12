# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingResetQtyDone(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_1")
        cls.location_src = cls.env.ref("stock.stock_location_suppliers")
        cls.location_dest = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")

    def _create_incoming_picking(self, qty=10.0):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.location_src.id,
                "location_dest_id": self.location_dest.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": qty,
                "quantity": qty,
                "picking_id": picking.id,
                "location_id": self.location_src.id,
                "location_dest_id": self.location_dest.id,
            }
        )
        return picking

    def test_01_clear_qty_resets_all_moves(self):
        """action_clear_qty sets quantity=0 on all non-done/cancel moves."""
        picking = self._create_incoming_picking(qty=10.0)
        self.assertEqual(picking.move_ids.quantity, 10.0)

        picking.action_clear_qty()

        self.assertEqual(picking.move_ids.quantity, 0.0)

    def test_02_cancelled_move_not_affected(self):
        """Cancelled moves are skipped by action_clear_qty."""
        picking = self._create_incoming_picking(qty=5.0)
        # Add a second move
        move2 = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 3.0,
                "quantity": 3.0,
                "picking_id": picking.id,
                "location_id": self.location_src.id,
                "location_dest_id": self.location_dest.id,
            }
        )
        move2._action_cancel()
        self.assertEqual(move2.state, "cancel")
        cancelled_qty = move2.quantity

        picking.action_clear_qty()

        # Cancelled move untouched
        self.assertEqual(move2.quantity, cancelled_qty)
        # Normal move cleared
        normal_move = picking.move_ids - move2
        self.assertEqual(normal_move.quantity, 0.0)

# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestPickingProgress(TransactionCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        picking = cls.env.ref("stock.outgoing_shipment_main_warehouse")
        cls.picking = picking.copy({"move_ids": [], "move_line_ids": []})
        cls.product = cls.env.ref("product.consu_delivery_01")
        cls.uom = cls.product.uom_id

    def add_move(self, name):
        data = {
            "name": name,
            "product_id": self.product.id,
            "product_uom_qty": 10,
            "product_uom": self.uom.id,
            "picking_id": self.picking.id,
            "location_id": self.picking.location_id.id,
            "location_dest_id": self.picking.location_dest_id.id,
        }
        return self.env["stock.move"].create(data)

    def set_quantity(self, moves, qty=None):
        for move in moves:
            if qty is None:
                quantity = move.product_uom_qty
            else:
                quantity = qty
            move.quantity = quantity

    def test_move_progress_creation(self):
        move = self.add_move("test_move_progress_on_creation")
        self.assertEqual(move.state, "draft")
        self.assertFalse(move.move_line_ids)
        self.assertFalse(move.picked)
        self.assertEqual(move.product_uom_qty, 10.0)
        self.assertEqual(move._get_picked_quantity(), 0.0)
        self.assertEqual(move.progress, 0.0)

    def test_move_progress_done_move(self):
        move = self.add_move("test_move_progress_done_move")
        # Need some qty and a picked move line before setting the move to done
        self.set_quantity(move, 1.0)
        move.move_line_ids.picked = True
        move._action_done(cancel_backorder=True)  # No backorder: keep original demand
        self.assertEqual(move.state, "done")
        self.assertTrue(move.move_line_ids)
        self.assertTrue(move.picked)
        self.assertEqual(move.product_uom_qty, 10.0)
        self.assertEqual(move._get_picked_quantity(), 1.0)
        self.assertEqual(move.progress, 100.0)  # Done move => progress is always 100%

    def test_move_progress_no_demanded_qty(self):
        move = self.add_move("test_move_progress_no_demanded_qty")
        move.product_uom_qty = 0.0
        self.assertEqual(move.state, "draft")
        self.assertFalse(move.move_line_ids)
        self.assertFalse(move.picked)
        self.assertEqual(move.product_uom_qty, 0.0)
        self.assertEqual(move._get_picked_quantity(), 0.0)
        self.assertEqual(move.progress, 100.0)  # No demand => progress is 100%

    def test_move_progress_picked(self):
        move = self.add_move("test_move_progress")
        self.set_quantity(move, 3.0)

        move.move_line_ids.picked = False
        self.assertEqual(move.state, "partially_available")
        self.assertTrue(move.move_line_ids)
        self.assertFalse(move.picked)
        self.assertEqual(move.product_uom_qty, 10.0)
        self.assertEqual(move._get_picked_quantity(), 3.0)
        self.assertEqual(move.progress, 0.0)  # Not picked => progress is 0%

        move.move_line_ids.picked = True
        self.assertEqual(move.state, "partially_available")
        self.assertTrue(move.move_line_ids)
        self.assertTrue(move.picked)
        self.assertEqual(move.product_uom_qty, 10.0)
        self.assertEqual(move._get_picked_quantity(), 3.0)
        self.assertEqual(move.progress, 30.0)  # Picked => progress is 30%

    def test_picking_progress(self):
        # No move, progress is 100%
        self.assertFalse(self.picking.move_ids)
        self.assertEqual(self.picking.progress, 100.0)
        # Add a new move, no qty done: progress 0%
        move1 = self.add_move("Move 1")
        self.assertEqual(self.picking.progress, 0.0)
        # Set quantity to 5.0 (half done), but the move is not picked: 0%
        self.set_quantity(move1, 5.0)
        self.assertEqual(self.picking.progress, 0.0)
        # Set the move as picked: 50%
        move1.picked = True
        self.assertEqual(self.picking.progress, 50.0)
        # Add a new move:
        # move1 progress is 50%
        # move2 progress is 0%
        # picking progress is 25%
        move2 = self.add_move("Move 2")
        self.assertEqual(self.picking.progress, 25.0)
        # Set quantity = 3.0 on move 2 and set it as picked
        # move1 progress is 50%
        # move2 progress is 30%
        # picking progress is 40%
        self.set_quantity(move2, 3.0)
        move2.picked = True
        self.assertEqual(self.picking.progress, 40.0)
        # Set quantity = 10.0 on both moves
        # move1 progress is 100%
        # move2 progress is 100%
        # picking progress is 100%
        self.set_quantity(move1 + move2, 10.0)
        self.assertEqual(self.picking.progress, 100.0)

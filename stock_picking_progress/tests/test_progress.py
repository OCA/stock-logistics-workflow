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

    def test_progress(self):
        # No move, progress is 100%
        self.assertEqual(self.picking.progress, 100.0)
        # Add a new move, no qty done -> picking 0%
        move1 = self.add_move("Move 1")
        self.assertEqual(self.picking.progress, 0.0)
        # Add a second move:
        move2 = self.add_move("Move 2")
        # Set quantity = 0.0 on both moves
        # Both moves = 0%, picking = 0%
        self.set_quantity(self.picking.move_ids, 0.0)
        self.assertEqual(move1.progress, 0.0)
        self.assertEqual(move2.progress, 0.0)
        self.assertEqual(self.picking.progress, 0.0)
        # Set quantity to 5.0 (half done)
        # move1 = 50%, move2 = 0%, picking = (50 + 0) / 2 = 25%
        self.set_quantity(move1, 5.0)
        self.assertEqual(move1.progress, 50.0)
        self.assertEqual(move2.progress, 0.0)
        self.assertEqual(self.picking.progress, 25.0)
        # Set quantity on move2 to 5.0 (half done)
        # move1 = 50%, move2 = 50%, picking = (50 + 50) / 2 = 50%
        self.set_quantity(move2, 5.0)
        self.assertEqual(move1.progress, 50.0)
        self.assertEqual(move2.progress, 50.0)
        self.assertEqual(self.picking.progress, 50.0)
        # Set quantity on move2 to its full demanded qty (10.0)
        # Since it's NOT done, move2 caps at 99.9 (not 100)
        # picking = (50 + 99.9) / 2 = 74.95
        self.set_quantity(move2)
        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(move1.state, "partially_available")
        self.assertEqual(move2.state, "assigned")
        self.assertEqual(move2.progress, 99.9)
        self.assertAlmostEqual(self.picking.progress, 74.95, places=2)
        # Set quantity on move1 to full demanded qty
        # Both moves = 99.9 (not done), picking = 99.9
        self.set_quantity(move1)
        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(move1.state, "assigned")
        self.assertEqual(move2.state, "assigned")
        self.assertEqual(move1.progress, 99.9)
        self.assertEqual(move2.progress, 99.9)
        self.assertEqual(self.picking.progress, 99.9)
        # Set picking to done
        self.picking.button_validate()
        self.picking._action_done()
        # Both moves = 100%, picking = 100%
        self.assertEqual(self.picking.state, "done")
        self.assertEqual(move1.state, "done")
        self.assertEqual(move2.state, "done")
        self.assertEqual(move1.progress, 100.0)
        self.assertEqual(move2.progress, 100.0)
        self.assertEqual(self.picking.progress, 100.0)

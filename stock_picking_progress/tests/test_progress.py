# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import SavepointCase


class TestPickingProgress(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        picking = cls.env.ref("stock.outgoing_shipment_main_warehouse")
        cls.picking = picking.copy({"move_lines": [], "move_line_ids": []})
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

    def set_quantity_done(self, moves, qty=None):
        for move in moves:
            if qty is None:
                quantity_done = move.product_uom_qty
            else:
                quantity_done = qty
            move.quantity_done = quantity_done

    def test_progress(self):
        # No move, progress is 100%
        self.assertEqual(self.picking.progress, 100.0)
        # Add a new move, no qty done: progress 0%
        move1 = self.add_move("Move 1")
        self.assertEqual(self.picking.progress, 0.0)
        # Set quantity_done to 5.0 (half done), both move and picking are 50% done
        self.set_quantity_done(move1, 5.0)
        self.assertEqual(self.picking.progress, 50.0)
        self.assertEqual(move1.progress, 50.0)
        # Add a new move:
        # move1 progress is still 50%
        # move2 progress is 0%
        # picking progress is 25%
        move2 = self.add_move("Move 2")
        self.assertEqual(self.picking.progress, 25.0)
        self.assertEqual(move1.progress, 50.0)
        self.assertEqual(move2.progress, 0.0)
        # Set quantity_done = 10.0 on move 2
        # move1 progress is still 50%
        # move2 progress is 100%
        # picking progress is 75%
        self.set_quantity_done(move2)
        self.assertEqual(self.picking.progress, 75.0)
        self.assertEqual(move2.progress, 100.0)
        # Set quantity_done = 10.0 on move 1
        # move1 progress is 100%
        # move2 progress is still 100%
        # picking progress is 100%
        self.set_quantity_done(move1)
        self.assertEqual(self.picking.progress, 100.0)
        self.assertEqual(move1.progress, 100.0)
        # Set quantity_done = 0.0 on both move
        # move1 progress is 0%
        # move2 progress is still 0%
        # picking progress is 0%
        self.set_quantity_done(self.picking.move_lines, 0.0)
        self.assertEqual(move1.progress, 0.0)
        self.assertEqual(move2.progress, 0.0)
        self.assertEqual(self.picking.progress, 0.0)

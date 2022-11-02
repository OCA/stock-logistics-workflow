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
        cls.move_line_model = cls.env["stock.move.line"]

    def add_line(self):
        data = {
            "product_id": self.product.id,
            "product_uom_qty": 10,
            "picking_id": self.picking.id,
            "product_uom_id": self.uom.id,
            "location_id": self.picking.location_id.id,
            "location_dest_id": self.picking.location_dest_id.id,
        }
        return self.move_line_model.create(data)

    def set_qty_done(self, move_lines, qty=None):
        for move_line in move_lines:
            if qty is None:
                qty_done = move_line.product_uom_qty
            else:
                qty_done = qty
            move_line.qty_done = qty_done

    def test_progress(self):
        # No line, progress is 0%
        self.assertEqual(self.picking.progress, 0.0)
        # Add a new line, no qty done: progress 0%
        line1 = self.add_line()
        self.assertEqual(self.picking.progress, 0.0)
        # Set qty_done to 5.0 (half done), both line and picking are 50% done
        self.set_qty_done(line1, 5.0)
        self.assertEqual(self.picking.progress, 50.0)
        self.assertEqual(line1.progress, 50.0)
        # Add a new line:
        # line1 progress is still 50%
        # line2 progress is 0%
        # picking progress is 25%
        line2 = self.add_line()
        self.assertEqual(self.picking.progress, 25.0)
        self.assertEqual(line1.progress, 50.0)
        self.assertEqual(line2.progress, 0.0)
        # Set qty_done = 10.0 on line 2
        # line1 progress is still 50%
        # line2 progress is 100%
        # picking progress is 75%
        self.set_qty_done(line2)
        self.assertEqual(self.picking.progress, 75.0)
        self.assertEqual(line2.progress, 100.0)
        # Set qty_done = 10.0 on line 1
        # line1 progress is 100%
        # line2 progress is still 100%
        # picking progress is 100%
        self.set_qty_done(line1)
        self.assertEqual(self.picking.progress, 100.0)
        self.assertEqual(line1.progress, 100.0)
        # Set qty_done = 0.0 on both lines
        # line1 progress is 0%
        # line2 progress is still 0%
        # picking progress is 0%
        self.set_qty_done(self.picking.move_line_ids, 0.0)
        self.assertEqual(line1.progress, 0.0)
        self.assertEqual(line2.progress, 0.0)
        self.assertEqual(self.picking.progress, 0.0)

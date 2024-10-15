# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Camptocamp SA - Julien Coux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import TestStockSplitPickingCase


class TestStockSplitPicking(TestStockSplitPickingCase):
    def test_stock_split_picking(self):
        # Picking state is draft
        self.assertEqual(self.picking.state, "draft")
        # We can't split a draft picking
        with self.assertRaises(UserError):
            self.picking.split_process()
        # Confirm picking
        self.picking.action_confirm()
        # We can't split an unassigned picking
        with self.assertRaises(UserError):
            self.picking.split_process()
        # We assign quantities in order to split
        self.picking.action_assign()
        move_line = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", self.picking.id),
                ("product_id", "=", self.product.id),
            ],
            limit=1,
        )
        move_line_2 = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", self.picking.id),
                ("product_id", "=", self.product_2.id),
            ],
            limit=1,
        )
        move_line.qty_done = 4.0
        # Split picking: 4 and 6
        # import pdb; pdb.set_trace()
        self.picking.split_process()

        # We have a picking with 4 units in state assigned
        self.assertAlmostEqual(move_line.qty_done, 4.0)
        self.assertAlmostEqual(move_line.reserved_qty, 4.0)
        self.assertAlmostEqual(move_line.reserved_uom_qty, 4.0)

        self.assertAlmostEqual(self.move.quantity_done, 4.0)
        self.assertAlmostEqual(self.move.product_qty, 4.0)
        self.assertAlmostEqual(self.move.product_uom_qty, 4.0)

        self.assertEqual(move_line.picking_id, self.picking)
        self.assertEqual(self.move.picking_id, self.picking)
        # move/move_line with no done qty no longer belongs to the original picking.
        self.assertNotEqual(move_line_2.picking_id, self.picking)
        self.assertNotEqual(self.move_2.picking_id, self.picking)

        self.assertEqual(self.picking.state, "assigned")
        # An another one with 6 units in state assigned
        new_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", self.picking.id)], limit=1
        )
        move_line = self.env["stock.move.line"].search(
            [("picking_id", "=", new_picking.id), ("product_id", "=", self.product.id)],
            limit=1,
        )
        move_line_2 = self.env["stock.move.line"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_2.id),
            ],
            limit=1,
        )

        self.assertAlmostEqual(move_line.qty_done, 0.0)
        self.assertAlmostEqual(move_line.reserved_qty, 6.0)
        self.assertAlmostEqual(move_line.reserved_uom_qty, 6.0)
        self.assertAlmostEqual(move_line_2.qty_done, 0.0)
        self.assertAlmostEqual(move_line_2.reserved_qty, 10.0)
        self.assertAlmostEqual(move_line_2.reserved_uom_qty, 10.0)

        move = self.env["stock.move"].search(
            [("picking_id", "=", new_picking.id), ("product_id", "=", self.product.id)],
            limit=1,
        )
        move_2 = self.env["stock.move"].search(
            [
                ("picking_id", "=", new_picking.id),
                ("product_id", "=", self.product_2.id),
            ],
            limit=1,
        )

        self.assertAlmostEqual(move.quantity_done, 0.0)
        self.assertAlmostEqual(move.product_qty, 6.0)
        self.assertAlmostEqual(move.product_uom_qty, 6.0)
        self.assertAlmostEqual(move_2.quantity_done, 0.0)
        self.assertAlmostEqual(move_2.product_qty, 10.0)
        self.assertAlmostEqual(move_2.product_uom_qty, 10.0)

        self.assertEqual(new_picking.state, "assigned")

    def test_stock_split_picking_wizard_move(self):
        self.move2 = self.move.copy()
        self.assertEqual(self.move2.picking_id, self.picking)
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=self.picking.ids)
            .create({"mode": "move"})
        )
        wizard.action_apply()
        self.assertNotEqual(self.move2.picking_id, self.picking)
        self.assertEqual(self.move.picking_id, self.picking)

    def test_stock_split_picking_wizard_selection(self):
        self.move2 = self.move.copy()
        self.assertEqual(self.move2.picking_id, self.picking)
        wizard = (
            self.env["stock.split.picking"]
            .with_context(active_ids=self.picking.ids)
            .create({"mode": "selection", "move_ids": [(6, False, self.move2.ids)]})
        )
        wizard.action_apply()
        self.assertNotEqual(self.move2.picking_id, self.picking)
        self.assertEqual(self.move.picking_id, self.picking)

    def test_stock_picking_split_off_moves(self):
        with self.assertRaises(UserError):
            # fails because we can't split off all lines
            self.picking._split_off_moves(self.picking.move_ids)
        with self.assertRaises(UserError):
            # fails because we can't split cancelled pickings
            self.picking.action_cancel()
            self.picking._split_off_moves(self.picking.move_ids)

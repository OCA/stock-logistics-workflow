# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2018 Camptocamp SA - Julien Coux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import RecordCapturer

from .common import TestStockSplitPickingCase


class TestStockSplitPicking(TestStockSplitPickingCase):
    def test_stock_split_picking_in_draft(self):
        # Picking state is draft
        self.assertEqual(self.picking.state, "draft")
        # We can't split a draft picking
        with self.assertRaisesRegex(UserError, "Nothing to split. Fill the quantities"):
            self._split_picking(self.picking, mode="quantity")

    def test_stock_split_picking_without_quantities(self):
        # Picking state is draft
        self.picking.action_confirm()
        # We can't split a draft picking
        with self.assertRaisesRegex(UserError, "Nothing to split. Fill the quantities"):
            self._split_picking(self.picking, mode="quantity")

    def test_stock_split_picking_with_nothing_left_to_split(self):
        # Confirm picking
        self.picking.action_confirm()
        for move in self.picking.move_ids:
            move.quantity = move.product_uom_qty
        # We can't split a draft picking
        with self.assertRaisesRegex(UserError, "Nothing to split, all demand is done."):
            self._split_picking(self.picking, mode="quantity")

    def test_stock_split_picking_consumable(self):
        # Confirm picking
        self.picking_consu.action_confirm()

        # Split picking: 4 and 6
        self.move_consu.quantity = 4.0
        self.move_consu_2.quantity = 0.0

        with (
            RecordCapturer(self.env["stock.picking"], []) as rc_picking,
            RecordCapturer(self.env["stock.move"], []) as rc_move,
        ):
            self._split_picking(self.picking_consu, mode="quantity")
            new_picking = rc_picking.records
            new_moves = rc_move.records

        # We have a new picking with 4 units in state assigned
        self.assertEqual(new_picking.state, "assigned")
        self.assertEqual(
            new_picking.move_ids,
            new_moves,
            "The new picking should have the new moves",
        )
        self.assertEqual(len(new_moves), 1, "Only one new move should be created")
        self.assertAlmostEqual(
            new_moves.quantity,
            4.0,
            "The new move should have the selected quantities",
        )
        self.assertAlmostEqual(
            new_moves.product_uom_qty,
            4.0,
            "The new move should have the selected quantities",
        )

        # And the backorder one is the original one, with the remaining quantities
        self.assertEqual(self.picking_consu.state, "confirmed")
        self.assertEqual(
            self.move_consu.picking_id,
            self.picking_consu,
            "The original move should be in the original picking",
        )
        self.assertEqual(
            self.move_consu_2.picking_id,
            self.picking_consu,
            "The original move should be in the original picking",
        )
        self.assertAlmostEqual(self.move_consu.quantity, 0.0)
        self.assertAlmostEqual(self.move_consu.product_uom_qty, 6.0)
        self.assertAlmostEqual(self.move_consu_2.quantity, 0.0)
        self.assertAlmostEqual(self.move_consu_2.product_uom_qty, 10.0)

    def test_stock_split_picking_product_wo_stock(self):
        # Confirm picking
        self.picking.action_confirm()

        # Split picking: 4 and 6
        self.move.quantity = 4.0
        self.move_2.quantity = 0.0

        with (
            RecordCapturer(self.env["stock.picking"], []) as rc_picking,
            RecordCapturer(self.env["stock.move"], []) as rc_move,
        ):
            self._split_picking(self.picking, mode="quantity")
            new_picking = rc_picking.records
            new_moves = rc_move.records

        # We have a new picking with 4 units in state assigned
        self.assertEqual(new_picking.state, "assigned")
        self.assertEqual(
            new_picking.move_ids,
            new_moves,
            "The new picking should have the new moves",
        )
        self.assertEqual(len(new_moves), 1, "Only one new move should be created")
        self.assertAlmostEqual(
            new_moves.quantity, 4.0, "The new move should have the selected quantities"
        )
        self.assertAlmostEqual(
            new_moves.product_uom_qty,
            4.0,
            "The new move should have the selected quantities",
        )

        # And the backorder one is the original one, with the remaining quantities
        self.assertEqual(self.picking.state, "confirmed")
        self.assertEqual(
            self.move.picking_id,
            self.picking,
            "The original move should be in the original picking",
        )
        self.assertEqual(
            self.move_2.picking_id,
            self.picking,
            "The original move should be in the original picking",
        )
        self.assertAlmostEqual(self.move.quantity, 0.0)
        self.assertAlmostEqual(self.move.product_uom_qty, 6.0)
        self.assertAlmostEqual(self.move_2.quantity, 0.0)
        self.assertAlmostEqual(self.move_2.product_uom_qty, 10.0)

    def test_stock_split_picking_product_with_stock(self):
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.src_location.id,
                "quantity": 4,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product_2.id,
                "location_id": self.src_location.id,
                "quantity": 4,
            }
        )

        # Confirm picking
        self.picking.action_confirm()

        # Split picking: 4 and 6
        self.move.quantity = 4.0
        self.move_2.quantity = 0.0

        with (
            RecordCapturer(self.env["stock.picking"], []) as rc_picking,
            RecordCapturer(self.env["stock.move"], []) as rc_move,
        ):
            self._split_picking(self.picking, mode="quantity")
            new_picking = rc_picking.records
            new_moves = rc_move.records

        # We have a new picking with 4 units in state assigned
        self.assertEqual(new_picking.state, "assigned")
        self.assertEqual(
            new_picking.move_ids,
            new_moves,
            "The new picking should have the new moves",
        )
        self.assertEqual(len(new_moves), 1, "Only one new move should be created")
        self.assertAlmostEqual(
            new_moves.quantity,
            4.0,
            "The new move should have the selected quantities",
        )
        self.assertAlmostEqual(
            new_moves.product_uom_qty,
            4.0,
            "The new move should have the selected quantities",
        )

        # And the backorder one is the original one, with the remaining quantities
        self.assertEqual(self.picking.state, "confirmed")
        self.assertEqual(
            self.move.picking_id,
            self.picking,
            "The original move should be in the original picking",
        )
        self.assertEqual(
            self.move_2.picking_id,
            self.picking,
            "The original move should be in the original picking",
        )
        self.assertAlmostEqual(self.move.quantity, 0.0)
        self.assertAlmostEqual(self.move.product_uom_qty, 6.0)
        self.assertAlmostEqual(self.move_2.quantity, 0.0)
        self.assertAlmostEqual(self.move_2.product_uom_qty, 10.0)

    def test_stock_split_picking_extract_entire_move(self):
        # Confirm picking
        self.picking_consu.action_confirm()

        # Split picking: the first move fully set, nothing on the second
        self.move_consu.quantity = self.move_consu.product_uom_qty
        self.move_consu_2.quantity = 0.0

        with (
            RecordCapturer(self.env["stock.picking"], []) as rc_picking,
            RecordCapturer(self.env["stock.move"], []) as rc_move,
        ):
            self._split_picking(self.picking_consu, mode="quantity")
            new_picking = rc_picking.records
            new_moves = rc_move.records

        # No new moves should have been created
        self.assertFalse(new_moves, "No new moves should have been created")

        # We have a new picking with the previous move that was fully set
        self.assertTrue(new_picking, "A new picking should have been created")
        self.assertEqual(new_picking.state, "assigned")
        self.assertEqual(
            new_picking.move_ids,
            self.move_consu,
            "The new picking should have the original move that was fully set",
        )

        # The moves quantities should be the same
        self.assertAlmostEqual(self.move_consu.quantity, 10.0)
        self.assertAlmostEqual(self.move_consu.product_uom_qty, 10.0)

        # And the backorder one is the original one, with the remaining quantities
        self.assertEqual(self.picking_consu.state, "confirmed")
        self.assertEqual(
            self.picking_consu.move_ids,
            self.move_consu_2,
            "The only remaining move should be in the original picking",
        )
        self.assertAlmostEqual(self.move_consu_2.quantity, 0.0)
        self.assertAlmostEqual(self.move_consu_2.product_uom_qty, 10.0)

    def test_stock_split_picking_ignore_cancelled_moves(self):
        # Confirm picking
        self.picking.action_confirm()

        # Split picking: 4 units on the first move, second is cancelled
        self.move.quantity = 4.0
        self.move_2._action_cancel()

        with (
            RecordCapturer(self.env["stock.picking"], []) as rc_picking,
            RecordCapturer(self.env["stock.move"], []) as rc_move,
        ):
            self._split_picking(self.picking, mode="quantity")
            new_picking = rc_picking.records
            new_moves = rc_move.records

        # We have a new picking with 4 units in state assigned
        self.assertEqual(new_picking.state, "assigned")
        self.assertEqual(
            new_picking.move_ids,
            new_moves,
            "The new picking should have the new moves",
        )
        self.assertEqual(len(new_moves), 1, "Only one new move should be created")
        self.assertAlmostEqual(
            new_moves.quantity,
            4.0,
            "The new move should have the selected quantities",
        )
        self.assertAlmostEqual(
            new_moves.product_uom_qty,
            4.0,
            "The new move should have the selected quantities",
        )

        # And the backorder one is the original one, with the remaining quantities
        # and the cancelled move
        self.assertEqual(self.picking.state, "confirmed")
        self.assertEqual(
            self.move.picking_id,
            self.picking,
            "The original move should be in the original picking",
        )
        self.assertEqual(
            self.move_2.picking_id,
            self.picking,
            "The original move should be in the original picking",
        )
        self.assertAlmostEqual(self.move.quantity, 0.0)
        self.assertAlmostEqual(self.move.product_uom_qty, 6.0)
        self.assertEqual(self.move_2.state, "cancel")

    def test_stock_split_picking_wizard_move_consumable(self):
        self.move2 = self.move_consu.copy()
        self.assertEqual(self.move2.picking_id, self.picking_consu)
        self._split_picking(self.picking_consu, mode="move")
        self.assertEqual(
            self.move2.picking_id,
            self.picking_consu,
            "Remaining move should be in original picking",
        )
        self.assertNotEqual(
            self.move_consu.picking_id,
            self.picking_consu,
            "Extracted move should be in new picking",
        )

    def test_stock_split_picking_wizard_move_product(self):
        self.move2 = self.move.copy()
        self.assertEqual(self.move2.picking_id, self.picking)
        self._split_picking(self.picking, mode="move")
        self.assertEqual(
            self.move2.picking_id,
            self.picking,
            "Remaining move should be in original picking",
        )
        self.assertNotEqual(
            self.move.picking_id,
            self.picking,
            "Extracted move should be in new picking",
        )

    def test_stock_split_picking_wizard_move_single_move(self):
        """Test move mode when picking has only one move"""
        # Create a picking with only one move
        picking = self._create_picking()
        self._create_stock_move(self.product, picking)
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            result = self._split_picking(picking, mode="move")

        self.assertFalse(rc_picking.records, "No new pickings should be created")
        self.assertEqual(result, True, "No action should be returned")

    def test_stock_split_picking_wizard_move_with_cancelled_move(self):
        """Test move mode when picking has cancelled moves"""
        # Create a picking where the first move is cancelled
        picking = self._create_picking()
        move1 = self._create_stock_move(self.product, picking)
        move1._action_cancel()
        move2 = self._create_stock_move(self.product, picking)
        move3 = self._create_stock_move(self.product_2, picking)
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="move")
            new_picking = rc_picking.records

        self.assertTrue(new_picking, "A new picking should be created")
        self.assertEqual(new_picking.state, "confirmed", "the new picking is confirmed")
        self.assertEqual(new_picking.move_ids, move2, "with the 1st non-cancelled move")
        self.assertEqual(move1.picking_id, picking, "the cancelled remains in original")
        self.assertEqual(move3.picking_id, picking, "the last one remains there, too")
        self.assertEqual(picking.state, "confirmed", "the picking remains confirmed")

    def test_stock_split_picking_wizard_move_with_only_one_cancelled_move(self):
        """Test move mode when picking has only one cancelled move remaining"""
        # Create a picking where the first move is cancelled
        picking = self._create_picking()
        move1 = self._create_stock_move(self.product, picking)
        move1._action_cancel()
        move2 = self._create_stock_move(self.product_2, picking)
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="move")
            new_picking = rc_picking.records

        self.assertTrue(new_picking, "A new picking should be created")
        self.assertEqual(new_picking.state, "confirmed", "the new picking is confirmed")
        self.assertEqual(new_picking.move_ids, move2, "with the 1st non-cancelled move")
        self.assertEqual(picking.move_ids, move1, "the cancelled remains in original")
        self.assertEqual(picking.state, "cancel", "the picking is cancelled")

    def test_stock_split_picking_wizard_move_with_only_cancelled_moves(self):
        """Test move mode when picking has only cancelled moves"""
        # Create a picking where the first move is cancelled
        picking = self._create_picking()
        move1 = self._create_stock_move(self.product, picking)
        move2 = self._create_stock_move(self.product_2, picking)
        (move1 + move2)._action_cancel()
        picking.action_confirm()

        with RecordCapturer(self.env["stock.picking"], []) as rc_picking:
            self._split_picking(picking, mode="move")
            new_picking = rc_picking.records

        self.assertFalse(new_picking, "No new picking should be created")
        self.assertEqual(picking.state, "cancel", "the picking is cancelled")

    def test_stock_split_picking_wizard_selection(self):
        self.move2 = self.move.copy()
        self.assertEqual(self.move2.picking_id, self.picking)
        self._split_picking(self.picking, mode="selection", move_ids=self.move2)
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

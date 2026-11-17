# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from unittest.mock import patch

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.stock_move_position.tests.common import StockMovePositionCommon


@tagged("post_install", "-at_install")
class TestStockPickingBatchMovePosition(StockMovePositionCommon):
    @classmethod
    def setUpClass(cls):
        """Number batches with the default step too."""
        super().setUpClass()
        cls.startClassPatcher(
            patch.object(
                type(cls.env["stock.picking.batch"]), "_line_numbering_step", 1
            )
        )

    def test_batch_picking_numbering(self):
        """A batch numbers its moves apart from the transfers' positions."""
        out_picking_1 = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        out_picking_2 = self._create_picking(
            self.out_type, [(self.product, 20), (self.product_2, 20)]
        )
        out_batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set([out_picking_1.id, out_picking_2.id])]}
        )
        out_batch.action_renumber_lines_positions()
        self.assertEqual(out_batch.move_ids[0].batch_position, "1")
        self.assertEqual(out_batch.move_ids[1].batch_position, "2")
        self.assertEqual(out_batch.move_ids[2].batch_position, "3")
        self.assertEqual(out_batch.move_ids[3].batch_position, "4")
        # position is a separate numbering axis: each picking was
        # already numbered on its own creation, independently of the
        # batch, so both pickings' moves share the same position
        # sequence — batch_position is what disambiguates them.
        self.assertEqual(out_picking_1.move_ids.mapped("position"), ["1", "2"])
        self.assertEqual(out_picking_2.move_ids.mapped("position"), ["1", "2"])

    def test_batch_auto_renumber_on_create(self):
        """Moves get batch positions when the batch is created."""
        out_picking_1 = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        out_picking_2 = self._create_picking(
            self.out_type, [(self.product, 20), (self.product_2, 20)]
        )
        out_batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set([out_picking_1.id, out_picking_2.id])]}
        )
        self.assertEqual(out_batch.move_ids[0].batch_position, "1")
        self.assertEqual(out_batch.move_ids[3].batch_position, "4")

    def test_batch_positions_grouped_per_picking(self):
        """Batch positions keep the moves of each transfer together.

        Scenario:
            1. Create a first transfer with two lines, then a second one.
            2. Sequence the first transfer's second line before its first
               one.
            3. Put both transfers in a batch.
        Expected:
            - The first transfer's lines get positions 1 and 2, following
              their sequence rather than their creation order.
            - The second transfer's line gets position 3.
        """
        out_picking_1 = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        moves_1 = out_picking_1.move_ids
        move_product = moves_1.filtered(lambda m: m.product_id == self.product)
        move_product_2 = moves_1.filtered(lambda m: m.product_id == self.product_2)
        # Set after the creation: modules like stock_picking_line_sequence
        # reset the sequences of a transfer's lines when a line is created.
        move_product.sequence = 20
        move_product_2.sequence = 10
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set([out_picking_1.id, out_picking_2.id])]}
        )
        self.assertEqual(move_product_2.batch_position, "1")
        self.assertEqual(move_product.batch_position, "2")
        self.assertEqual(out_picking_2.move_ids.batch_position, "3")

    def test_batch_picking_added_last(self):
        """A transfer added to a batch goes after the ones already in it.

        Scenario:
            1. Create a first transfer, then a second one.
            2. Put the second transfer in a batch.
            3. Add the first transfer to the batch.
        Expected:
            - The second transfer keeps position 1.
            - The first transfer gets position 2, although it is older.
        """
        out_picking_1 = self._create_picking(self.out_type, [(self.product, 10)])
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        out_batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(out_picking_2.ids)]}
        )
        out_picking_1.write({"batch_id": out_batch.id})
        self.assertEqual(out_picking_2.move_ids.batch_position, "1")
        self.assertEqual(out_picking_1.move_ids.batch_position, "2")

    def test_batch_renumber_on_picking_reorder(self):
        """Reordering the transfers of a batch renumbers its lines.

        Scenario:
            1. Put two transfers in a batch.
            2. Move the second transfer before the first one.
        Expected:
            - The second transfer's line gets position 1.
            - The first transfer's line gets position 2.
        """
        out_picking_1 = self._create_picking(self.out_type, [(self.product, 10)])
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        out_batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set([out_picking_1.id, out_picking_2.id])]}
        )
        out_batch.write(
            {
                "picking_ids": [
                    Command.update(out_picking_2.id, {"batch_sequence": 1}),
                    Command.update(out_picking_1.id, {"batch_sequence": 2}),
                ]
            }
        )
        self.assertEqual(out_picking_2.move_ids.batch_position, "1")
        self.assertEqual(out_picking_1.move_ids.batch_position, "2")

    def test_batch_auto_renumber_on_move_added_to_batched_picking(self):
        """A line added to a transfer already in a batch gets a batch position.

        Scenario:
            1. Put two transfers with one line each in a batch.
            2. Add a line to the first transfer.
        Expected:
            - The new line gets a batch position, right after the first
              transfer's other line.
            - The second transfer's line moves to position 3.
        """
        out_picking_1 = self._create_picking(self.out_type, [(self.product, 10)])
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set([out_picking_1.id, out_picking_2.id])]}
        )
        new_move = self.env["stock.move"].create(
            {
                "picking_id": out_picking_1.id,
                "product_id": self.product_2.id,
                "product_uom_qty": 10,
                "product_uom": self.product_2.uom_id.id,
                "location_id": self.out_type.default_location_src_id.id,
                "location_dest_id": self.out_type.default_location_dest_id.id,
            }
        )
        self.assertEqual(new_move.batch_position, "2")
        self.assertEqual(out_picking_2.move_ids.batch_position, "3")

    def test_batch_renumber_on_move_moved_to_other_batch(self):
        """A line moved to a transfer of another batch gets a new position.

        Scenario:
            1. Put a transfer with two lines in a first batch.
            2. Put a transfer with one line in a second batch.
            3. Move the first line of the first transfer to the second one.
        Expected:
            - The second batch is renumbered: its two lines get positions
              1 and 2, instead of both keeping 1.
        """
        out_picking_1 = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(out_picking_1.ids)]}
        )
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(out_picking_2.ids)]}
        )
        moved = out_picking_1.move_ids.filtered(lambda m: m.product_id == self.product)
        moved.write({"picking_id": out_picking_2.id})
        self.assertEqual(
            sorted(out_picking_2.move_ids.mapped("batch_position")), ["1", "2"]
        )

    def test_batch_pickings_added_together_get_distinct_sequences(self):
        """Transfers added to a batch together are ordered among themselves.

        Scenario:
            1. Create two transfers and put them in a batch in one go.
        Expected:
            - Each transfer gets its own sequence, the older one first.
        """
        out_picking_1 = self._create_picking(self.out_type, [(self.product, 10)])
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set([out_picking_1.id, out_picking_2.id])]}
        )
        self.assertLess(out_picking_1.batch_sequence, out_picking_2.batch_sequence)

    def test_batch_auto_renumber_on_picking_write_batch_id(self):
        """Transfers attached by writing their batch get batch positions."""
        # Mirrors stock_picking_batch's "Add to batch" wizard
        # (stock.picking.to.batch.attach_pickings()), which creates an
        # empty batch then attaches existing pickings by writing
        # batch_id on the pickings, never touching the batch's own
        # picking_ids field.
        out_picking_1 = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        out_picking_2 = self._create_picking(
            self.out_type, [(self.product, 20), (self.product_2, 20)]
        )
        out_batch = self.env["stock.picking.batch"].create({})
        (out_picking_1 | out_picking_2).write({"batch_id": out_batch.id})
        self.assertEqual(out_batch.move_ids[0].batch_position, "1")
        self.assertEqual(out_batch.move_ids[3].batch_position, "4")

    def test_done_batch_still_renumbers(self):
        """A done batch can still be renumbered."""
        out_picking = self._create_picking(self.out_type, [(self.product, 10)])
        out_batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(out_picking.ids)]}
        )
        out_batch.state = "done"
        out_batch.action_renumber_lines_positions()
        self.assertEqual(out_batch.move_ids.batch_position, "1")

    def test_split_keeps_batch_position(self):
        """A split move keeps the batch position of the original move."""
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(picking.ids)]}
        )
        picking.action_confirm()
        move = picking.move_ids
        self.assertEqual(move.batch_position, "1")
        new_move = self.env["stock.move"].create(move._split(4))
        self.assertEqual(new_move.batch_position, "1")

    def test_order_by_batch_position_is_numeric(self):
        """Moves sorted by batch position follow the numbers, not the text.

        Scenario:
            1. Put a transfer with 10 lines in a batch (batch positions 1 to
               10).
            2. Sort its moves by batch position.
        Expected:
            - Batch position 10 comes last, not right after 1.
        """
        picking = self._create_picking(self.out_type, [(self.product, 1)] * 10)
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(picking.ids)]}
        )
        moves = self.env["stock.move"].search(
            [("picking_id", "=", picking.id)], order="batch_position"
        )
        self.assertEqual(moves.mapped("batch_position")[-2:], ["9", "10"])

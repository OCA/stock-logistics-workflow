# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.fields import Command
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockMovePosition(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Products and operation types used by the tests."""
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls._create_product("Test product", "TEST")
        cls.product_2 = cls._create_product("Test product 2", "TEST2")
        cls.out_type = cls.env.ref("stock.picking_type_out")
        cls.in_type = cls.env.ref("stock.picking_type_in")
        cls.out_dest = cls.out_type.default_location_dest_id

    @classmethod
    def _create_product(cls, name, code):
        """Create a storable product."""
        return cls.env["product.product"].create(
            {
                "name": name,
                "default_code": code,
                "type": "consu",
                "is_storable": True,
                "list_price": 10.0,
            }
        )

    @classmethod
    def _create_picking(cls, picking_type, lines_spec):
        """Create a transfer with one move per (product, qty) spec."""
        src = picking_type.default_location_src_id
        dest = picking_type.default_location_dest_id
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": line_spec[0].id,
                            "product_uom_qty": line_spec[1],
                            "product_uom": line_spec[0].uom_id.id,
                            "location_id": src.id,
                            "location_dest_id": dest.id,
                        }
                    )
                    for line_spec in lines_spec
                ],
            }
        )

    def test_picking_numbering(self):
        """The renumber action numbers the moves of any transfer type."""
        out_picking = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        out_picking.action_renumber_lines_positions()
        self.assertEqual(out_picking.move_ids[0].position, "10")
        self.assertEqual(out_picking.move_ids[1].position, "20")
        in_picking = self._create_picking(
            self.in_type, [(self.product, 10), (self.product_2, 10)]
        )
        in_picking.action_renumber_lines_positions()
        self.assertEqual(in_picking.move_ids[0].position, "10")
        self.assertEqual(in_picking.move_ids[1].position, "20")

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
        self.assertEqual(out_batch.move_ids[0].batch_position, "10")
        self.assertEqual(out_batch.move_ids[1].batch_position, "20")
        self.assertEqual(out_batch.move_ids[2].batch_position, "30")
        self.assertEqual(out_batch.move_ids[3].batch_position, "40")
        # position is a separate numbering axis: each picking was
        # already numbered on its own creation, independently of the
        # batch, so both pickings' moves share the same position
        # sequence — batch_position is what disambiguates them.
        self.assertEqual(out_picking_1.move_ids.mapped("position"), ["10", "20"])
        self.assertEqual(out_picking_2.move_ids.mapped("position"), ["10", "20"])

    def test_auto_renumber_on_create(self):
        """Moves are numbered when the transfer is created."""
        picking = self._create_picking(
            self.out_type, [(self.product, 10), (self.product_2, 10)]
        )
        self.assertEqual(picking.move_ids[0].position, "10")
        self.assertEqual(picking.move_ids[1].position, "20")

    def test_auto_renumber_on_write_add_line(self):
        """A move added through the transfer is numbered after the others."""
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        picking.write(
            {
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product_2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_2.uom_id.id,
                            "location_id": self.out_type.default_location_src_id.id,
                            "location_dest_id": self.out_dest.id,
                        }
                    )
                ]
            }
        )
        self.assertEqual(picking.move_ids[0].position, "10")
        self.assertEqual(picking.move_ids[1].position, "20")

    def test_auto_renumber_on_move_create_with_existing_picking(self):
        """A move created in an existing transfer is numbered."""
        # Mirrors purchase_stock's _create_or_update_picking(), which
        # creates the new stock.move with picking_id already set on an
        # existing, already-numbered picking.
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "product_id": self.product_2.id,
                "product_uom_qty": 10,
                "product_uom": self.product_2.uom_id.id,
                "location_id": self.out_type.default_location_src_id.id,
                "location_dest_id": self.out_type.default_location_dest_id.id,
            }
        )
        self.assertEqual(picking.move_ids[0].position, "10")
        self.assertEqual(picking.move_ids[1].position, "20")

    def test_auto_renumber_on_move_write_picking_id(self):
        """A move assigned to a transfer afterwards is numbered."""
        # Mirrors stock.move._assign_picking(), which creates the move
        # without a picking_id and assigns it afterwards via write().
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        new_move = self.env["stock.move"].create(
            {
                "product_id": self.product_2.id,
                "product_uom_qty": 10,
                "product_uom": self.product_2.uom_id.id,
                "location_id": self.out_type.default_location_src_id.id,
                "location_dest_id": self.out_type.default_location_dest_id.id,
            }
        )
        self.assertFalse(new_move.position)
        new_move.write({"picking_id": picking.id})
        self.assertEqual(picking.move_ids[0].position, "10")
        self.assertEqual(picking.move_ids[1].position, "20")

    def test_done_picking_still_renumbers(self):
        """A done transfer can still be renumbered."""
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        picking.state = "done"
        picking.action_renumber_lines_positions()
        self.assertEqual(picking.move_ids.position, "10")

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
        self.assertEqual(out_batch.move_ids[0].batch_position, "10")
        self.assertEqual(out_batch.move_ids[3].batch_position, "40")

    def test_batch_positions_grouped_per_picking(self):
        """Batch positions keep the moves of each transfer together.

        Scenario:
            1. Create a first transfer, then a second one.
            2. Add a second line to the first transfer, sequenced before
               its existing line.
            3. Put both transfers in a batch.
        Expected:
            - The first transfer's lines get positions 10 and 20, following
              their sequence rather than their creation order.
            - The second transfer's line gets position 30.
        """
        out_picking_1 = self._create_picking(self.out_type, [(self.product, 10)])
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        out_picking_1.move_ids.sequence = 20
        out_picking_1.write(
            {
                "move_ids": [
                    Command.create(
                        {
                            "sequence": 10,
                            "product_id": self.product_2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_2.uom_id.id,
                            "location_id": self.out_type.default_location_src_id.id,
                            "location_dest_id": self.out_dest.id,
                        }
                    )
                ]
            }
        )
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set([out_picking_1.id, out_picking_2.id])]}
        )
        moves_1 = out_picking_1.move_ids
        move_product = moves_1.filtered(lambda m: m.product_id == self.product)
        move_product_2 = moves_1.filtered(lambda m: m.product_id == self.product_2)
        self.assertEqual(move_product_2.batch_position, "10")
        self.assertEqual(move_product.batch_position, "20")
        self.assertEqual(out_picking_2.move_ids.batch_position, "30")

    def test_batch_picking_added_last(self):
        """A transfer added to a batch goes after the ones already in it.

        Scenario:
            1. Create a first transfer, then a second one.
            2. Put the second transfer in a batch.
            3. Add the first transfer to the batch.
        Expected:
            - The second transfer keeps position 10.
            - The first transfer gets position 20, although it is older.
        """
        out_picking_1 = self._create_picking(self.out_type, [(self.product, 10)])
        out_picking_2 = self._create_picking(self.out_type, [(self.product, 20)])
        out_batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(out_picking_2.ids)]}
        )
        out_picking_1.write({"batch_id": out_batch.id})
        self.assertEqual(out_picking_2.move_ids.batch_position, "10")
        self.assertEqual(out_picking_1.move_ids.batch_position, "20")

    def test_batch_renumber_on_picking_reorder(self):
        """Reordering the transfers of a batch renumbers its lines.

        Scenario:
            1. Put two transfers in a batch.
            2. Move the second transfer before the first one.
        Expected:
            - The second transfer's line gets position 10.
            - The first transfer's line gets position 20.
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
        self.assertEqual(out_picking_2.move_ids.batch_position, "10")
        self.assertEqual(out_picking_1.move_ids.batch_position, "20")

    def test_batch_auto_renumber_on_move_added_to_batched_picking(self):
        """A line added to a transfer already in a batch gets a batch position.

        Scenario:
            1. Put two transfers with one line each in a batch.
            2. Add a line to the first transfer.
        Expected:
            - The new line gets a batch position, right after the first
              transfer's other line.
            - The second transfer's line moves to position 30.
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
        self.assertEqual(new_move.batch_position, "20")
        self.assertEqual(out_picking_2.move_ids.batch_position, "30")

    def test_batch_renumber_on_move_moved_to_other_batch(self):
        """A line moved to a transfer of another batch gets a new position.

        Scenario:
            1. Put a transfer with two lines in a first batch.
            2. Put a transfer with one line in a second batch.
            3. Move the first line of the first transfer to the second one.
        Expected:
            - The second batch is renumbered: its two lines get positions
              10 and 20, instead of both keeping 10.
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
            sorted(out_picking_2.move_ids.mapped("batch_position")), ["10", "20"]
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

    def test_order_by_batch_position_is_numeric(self):
        """Sorting moves by batch position follows the numbers, not the text.

        Scenario:
            1. Put a transfer with 10 lines in a batch (positions 10 to 100).
            2. Sort its lines by batch position.
        Expected:
            - Position 100 comes last, not right after 10.
        """
        out_picking = self._create_picking(self.out_type, [(self.product, 1)] * 10)
        self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(out_picking.ids)]}
        )
        moves = self.env["stock.move"].search(
            [("picking_id", "=", out_picking.id)], order="batch_position"
        )
        self.assertEqual(moves[-1].batch_position, "100")

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
        self.assertEqual(out_batch.move_ids[0].batch_position, "10")
        self.assertEqual(out_batch.move_ids[3].batch_position, "40")

    def test_done_batch_still_renumbers(self):
        """A done batch can still be renumbered."""
        out_picking = self._create_picking(self.out_type, [(self.product, 10)])
        out_batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(out_picking.ids)]}
        )
        out_batch.state = "done"
        out_batch.action_renumber_lines_positions()
        self.assertEqual(out_batch.move_ids.batch_position, "10")

    def test_split_keeps_positions(self):
        """A split move keeps the position of the original move."""
        picking = self._create_picking(self.out_type, [(self.product, 10)])
        picking.action_confirm()
        move = picking.move_ids
        self.assertEqual(move.position, "10")
        new_move = self.env["stock.move"].create(move._split(4))
        self.assertEqual(new_move.position, "10")

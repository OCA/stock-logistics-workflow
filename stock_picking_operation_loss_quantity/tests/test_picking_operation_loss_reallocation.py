# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import OperationLossQuantityCommon


class TestPickingOperationLossNewReservation(OperationLossQuantityCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shelf_a = cls.env["stock.location"].create(
            {
                "name": "Shelf A",
                "usage": "internal",
                "location_id": cls.loc_stock.id,
            }
        )
        cls.shelf_b = cls.env["stock.location"].create(
            {
                "name": "Shelf B",
                "usage": "internal",
                "location_id": cls.loc_stock.id,
            }
        )
        cls._create_quantities(cls.product_2, 5.0, location=cls.shelf_a)
        cls._create_quantities(cls.product_2, 2.0, location=cls.shelf_b)

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.pick_type_out.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking.id,
                "name": "Test Fallback Move",
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 5,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
            }
        )
        cls.move._action_confirm()
        cls.picking.action_assign()

    def test_loss_quantity_auto_reallocation(self):
        initial_line = self.move.move_line_ids[0]
        self.assertEqual(initial_line.location_id, self.shelf_a)

        initial_line.action_lose_quantity()

        # Nothing was ever done on the shelf A line: it is dropped and the
        # whole demand is re-reserved on the only other available stock.
        self.assertNotIn(initial_line, self.move.move_line_ids)
        self.assertEqual(len(self.move.move_line_ids), 1)
        new_line = self.move.move_line_ids[0]
        self.assertEqual(new_line.location_id, self.shelf_b)
        self.assertEqual(new_line.reserved_uom_qty, 2.0)

        locked_moves = self.env["stock.move"].search(
            [("quant_lock_quant_id", "!=", False)],
            order="id desc",
            limit=1,
        )
        self.assertTrue(locked_moves)
        self.assertTrue(locked_moves.quant_lock_quant_id.is_locked_by_picking)

    def test_loss_quantity_partially_processed_move_auto_reallocation(self):
        self.move.product_uom_qty = 7.0
        self.picking.action_assign()

        self.assertEqual(len(self.move.move_line_ids), 2)
        line_shelf_a = self.move.move_line_ids.filtered(
            lambda l: l.location_id == self.shelf_a
        )
        line_shelf_b = self.move.move_line_ids.filtered(
            lambda l: l.location_id == self.shelf_b
        )
        self.assertEqual(line_shelf_a.reserved_uom_qty, 5.0)
        self.assertEqual(line_shelf_b.reserved_uom_qty, 2.0)

        line_shelf_a.qty_done = 5.0
        line_shelf_b.action_lose_quantity()

        # Nothing else is available anywhere: no new line is created, so the
        # now-empty shelf B line is kept as a visible placeholder instead of
        # being silently dropped.
        self.assertIn(line_shelf_b, self.move.move_line_ids)
        self.assertEqual(len(self.move.move_line_ids), 2)
        lock_moves = self.env["stock.move"].search(
            [("quant_lock_quant_id", "!=", False)],
            order="id desc",
            limit=1,
        )
        self.assertTrue(lock_moves.quant_lock_quant_id.is_locked_by_picking)

    def test_loss_quantity_auto_reallocation_same_location_different_lot(self):
        self.initiate_values()
        self.move_1.product_uom_qty = 3.0
        self.picking_1.action_assign()

        self.assertEqual(len(self.picking_1.move_line_ids), 1)
        initial_line = self.picking_1.move_line_ids
        self.assertEqual(initial_line.lot_id, self.product_1_lotA)

        initial_line.action_lose_quantity()

        # Nothing was ever done on the lotA line: it is dropped and the
        # demand is re-reserved on the only other available lot.
        self.assertEqual(len(self.picking_1.move_line_ids), 1)
        self.assertEqual(self.picking_1.move_line_ids.lot_id, self.product_1_lotB)
        lock_moves = self.env["stock.move"].search(
            [("quant_lock_quant_id", "!=", False)],
            order="id desc",
            limit=1,
        )
        self.assertTrue(lock_moves.quant_lock_quant_id.is_locked_by_picking)

    def test_loss_quantity_rereserve_creates_new_line_for_previously_done_lot(self):
        self.initiate_values()
        # `_create_quantities` sets the counted quantity for the quant
        # (inventory adjustment semantics), it does not add to the existing
        # stock: initiate_values() already put 3 units of lotA in stock, so
        # the target here is 3 + 2 = 5 to make 2 extra units available.
        self._create_quantities(self.product_1, 5.0, lot=self.product_1_lotA)

        self.assertEqual(len(self.picking_1.move_line_ids), 2)
        line_lot_a = self.picking_1.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        line_lot_b = self.picking_1.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )

        line_lot_a.qty_done = line_lot_a.reserved_uom_qty
        line_lot_b.qty_done = 2.0

        line_lot_b.action_lose_quantity()

        self.assertEqual(line_lot_a.qty_done, 3.0)
        self.assertEqual(line_lot_a.reserved_uom_qty, 3.0)
        self.assertIn(line_lot_a, self.picking_1.move_line_ids)

        self.assertEqual(line_lot_b.qty_done, 2.0)
        self.assertEqual(line_lot_b.reserved_uom_qty, 2.0)
        self.assertIn(line_lot_b, self.picking_1.move_line_ids)

        lot_a_lines = self.picking_1.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        self.assertEqual(len(lot_a_lines), 2)

        rereserved_line = lot_a_lines - line_lot_a
        self.assertEqual(len(rereserved_line), 1)
        self.assertEqual(rereserved_line.qty_done, 0)
        self.assertEqual(rereserved_line.reserved_uom_qty, 2.0)

        loss_pickings = self._get_loss_pickings()
        self.assertEqual(len(loss_pickings), 1)
        self.assertTrue(loss_pickings.move_ids.filtered("quant_lock_quant_id"))

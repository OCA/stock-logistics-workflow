# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from .common import OperationLossQuantityCommon


class TestQuantityLossTracking(OperationLossQuantityCommon):
    def test_initiate_values_initial_situation(self):
        self.initiate_values()
        lines = self.picking_1.move_line_ids
        self.assertEqual(len(lines), 2)
        line_lotA = lines.filtered(lambda line: line.lot_id == self.product_1_lotA)
        line_lotB = lines.filtered(lambda line: line.lot_id == self.product_1_lotB)
        self.assertEqual(line_lotA.reserved_uom_qty, 3)
        self.assertEqual(line_lotB.reserved_uom_qty, 4)

    def test_loss_line_tracking(self):
        self.initiate_values()

        lines = self.picking_1.move_line_ids
        line_lot_a = lines.filtered(lambda line: line.lot_id == self.product_1_lotA)
        line_lot_b = lines.filtered(lambda line: line.lot_id == self.product_1_lotB)

        quants_available_quantity_lot_b_before = self._get_quants_available_qty(
            line_lot_b
        )

        line_lot_a.qty_done = 1.0
        line_lot_b.qty_done = 2.0
        line_lot_b.action_lose_quantity()

        quants_available_quantity_lot_b_after = self._get_quants_available_qty(
            line_lot_b
        )

        self.assertEqual(quants_available_quantity_lot_b_after, 0)
        self.assertEqual(quants_available_quantity_lot_b_before, 1)

        self.assertEqual(line_lot_b.reserved_qty, 2.0)
        self.assertEqual(line_lot_b.qty_done, line_lot_b.reserved_qty)
        # line_lot_a is unrelated to the loss declared on line_lot_b: it is
        # left untouched, still partially processed.
        self.assertEqual(3.0, line_lot_a.reserved_qty)
        self.assertEqual(1.0, line_lot_a.qty_done)

        loss_pickings = self._get_loss_pickings()
        self.assertEqual(1, len(loss_pickings))
        lock_moves = loss_pickings.move_ids.filtered("quant_lock_quant_id")
        self.assertTrue(lock_moves)
        self.assertTrue(lock_moves.filtered(lambda m: m.product_id == self.product_1))

    def test_loss_line_tracking_no_new_line(self):
        self.initiate_values()
        lines = self.picking_1.move_line_ids
        self.assertEqual(len(lines), 2)
        line_lot_a = lines.filtered(lambda line: line.lot_id == self.product_1_lotA)
        line_lot_b = lines.filtered(lambda line: line.lot_id == self.product_1_lotB)
        # we partially process line_lot_a
        line_lot_a.qty_done = line_lot_a.reserved_uom_qty - 1
        # we fully process line_lot_b
        line_lot_b.qty_done = line_lot_b.reserved_uom_qty

        # declare loss on the same move line, a new move line is created
        # since our picking is for 7 units and we have 8 units in stock
        # in 2 diffrent lots. If we declare a loss on line_lot_a,
        # we still have 1 unit in stock on lot_b
        line_lot_a.action_lose_quantity()

        self.assertEqual(line_lot_a.reserved_qty, line_lot_a.qty_done)
        lines = self.picking_1.move_line_ids
        self.assertEqual(len(lines), 3)
        new_line = lines - line_lot_a - line_lot_b
        self.assertEqual(new_line.lot_id, self.product_1_lotB)
        self.assertEqual(new_line.reserved_uom_qty, 1.0)
        # if we declare a loss on line_lot_b, we should not create a new line
        # since we have no more stock available and we have not processed
        # any quantity on line_lot_b,
        new_line.action_lose_quantity()
        self.assertFalse(new_line.exists())

    def test_loss_line_tracking_with_pack(self):
        self.initiate_values()
        lines = self.picking_1.move_line_ids

        line_lot_a = lines.filtered(lambda line: line.lot_id == self.product_1_lotA)
        line_lot_b = lines.filtered(lambda line: line.lot_id == self.product_1_lotB)
        line_lot_a.qty_done = 1.0
        line_lot_b.qty_done = 2.0

        self.picking_1._put_in_pack(line_lot_a | line_lot_b)
        lines = self.picking_1.move_line_ids
        self.assertEqual(len(lines), 4)
        line_lot_a_no_pack = lines.filtered(
            lambda line: line.lot_id == self.product_1_lotA
            and not line.package_level_id
        )
        line_lot_b_no_pack = lines.filtered(
            lambda line: line.lot_id == self.product_1_lotB
            and not line.package_level_id
        )
        line_lot_a_pack = lines.filtered(
            lambda line: line.lot_id == self.product_1_lotA and line.package_level_id
        )
        line_lot_b_pack = lines.filtered(
            lambda line: line.lot_id == self.product_1_lotB and line.package_level_id
        )

        self.assertEqual(line_lot_a_no_pack.qty_done, 0)
        self.assertEqual(line_lot_a, line_lot_a_no_pack)
        self.assertEqual(line_lot_b_no_pack.qty_done, 0)
        self.assertEqual(line_lot_b, line_lot_b_no_pack)
        self.assertEqual(line_lot_a_pack.qty_done, 1)
        self.assertEqual(line_lot_b_pack.qty_done, 2)

        quants_available_quantity_lot_a_before = self._get_quants_available_qty(
            line_lot_a_pack
        )

        line_lot_a_no_pack.action_lose_quantity()

        quants_available_quantity_lot_a_after = self._get_quants_available_qty(
            line_lot_a_pack
        )

        self.assertEqual(quants_available_quantity_lot_a_after, 0)
        self.assertGreaterEqual(quants_available_quantity_lot_a_before, 0)

        self.assertEqual(len(self.picking_1.move_line_ids), 3)
        loss_pickings = self._get_loss_pickings()
        self.assertEqual(1, len(loss_pickings))
        lock_moves = loss_pickings.move_ids.filtered("quant_lock_quant_id")
        self.assertTrue(lock_moves)
        self.assertTrue(lock_moves.filtered(lambda m: m.product_id == self.product_1))

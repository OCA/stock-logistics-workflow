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

        self.assertEqual(
            quants_available_quantity_lot_b_before,
            quants_available_quantity_lot_b_after,
        )

        # The remaining line on original picking should have the reserved
        # quantity == the done quantity
        self.assertEqual(line_lot_b.reserved_qty, 2.0)
        self.assertEqual(line_lot_b.qty_done, line_lot_b.reserved_qty)

        # Nothing happened to product 1
        self.assertEqual(3.0, line_lot_a.reserved_qty)
        self.assertEqual(1.0, line_lot_a.qty_done)

        loss_pickings = self._get_loss_pickings()

        self.assertEqual(1, len(loss_pickings))
        loss_line_lot_b = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )
        self.assertTrue(loss_line_lot_b)
        self.assertEqual(loss_line_lot_b.state, "assigned")
        self.assertEqual(loss_line_lot_b.reserved_uom_qty, 2)

        loss_line_lot_a = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        self.assertFalse(loss_line_lot_a)
        # make an inventory adjustment and check that the loss picking is now
        # cancelled
        self._create_quantities(
            product=loss_line_lot_b.product_id,
            quantity=loss_line_lot_b.reserved_uom_qty,
            location=loss_line_lot_b.location_id,
            lot=loss_line_lot_b.lot_id,
            package=loss_line_lot_b.package_id,
        )
        self.assertEqual(loss_pickings.state, "cancel")

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

        self.assertEqual(
            quants_available_quantity_lot_a_before,
            quants_available_quantity_lot_a_after,
        )

        self.assertEqual(len(self.picking_1.move_line_ids), 3)
        self.assertNotIn(line_lot_a_no_pack.id, self.picking_1.move_line_ids.ids)

        self.assertEqual(2.0, line_lot_b.reserved_qty)
        self.assertEqual(0.0, line_lot_b.qty_done)

        loss_pickings = self._get_loss_pickings()

        self.assertEqual(1, len(loss_pickings))
        loss_line_lot_a = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        self.assertTrue(loss_line_lot_a)
        self.assertEqual(loss_line_lot_a.state, "assigned")
        self.assertEqual(loss_line_lot_a.reserved_uom_qty, 2)

        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )
        self.assertFalse(line)

        # make an inventory adjustment and check that the loss picking is now
        # cancelled
        self._create_quantities(
            product=loss_line_lot_a.product_id,
            quantity=loss_line_lot_a.reserved_uom_qty,
            location=loss_line_lot_a.location_id,
            lot=loss_line_lot_a.lot_id,
            package=loss_line_lot_a.package_id,
        )
        self.assertEqual(loss_pickings.state, "cancel")

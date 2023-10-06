# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import TransactionCase

from .common import OperationLossQuantityCommon


class TestQuantityLossTracking(OperationLossQuantityCommon, TransactionCase):
    def test_loss_line_tracking(self):
        self.initiate_values()
        self.picking_1.action_assign()

        lines = self.picking_1.move_line_ids
        self.assertEqual(len(lines), 2)

        line_lot_a = lines.filtered(lambda line: line.lot_id == self.product_1_lotA)
        line_lot_b = lines.filtered(lambda line: line.lot_id == self.product_1_lotB)
        line_lot_b.qty_done = 2.0
        line_lot_a.qty_done = 1.0
        line_lot_a.action_loss_quantity()

        done_line = self.picking_1.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )

        # The remaining line on original picking should have the reserved
        # quantity == the done quantity
        self.assertEqual(done_line.reserved_qty, 1.0)  # Original qty == 3.0 - 2.0 loss
        self.assertEqual(done_line.qty_done, 1)

        # Nothing happened to product 1
        self.assertEqual(4.0, line_lot_b.reserved_qty)
        self.assertEqual(2.0, line_lot_b.qty_done)

        loss_pickings = self._get_loss_pickings()

        self.assertEqual(1, len(loss_pickings))
        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        self.assertTrue(line)
        self.assertEqual(line.state, "assigned")
        self.assertEqual(line.reserved_uom_qty, 2)

        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )
        self.assertFalse(line)

    def test_loss_line_tracking_with_pack(self):
        """
        Confirm and assign the picking 1

        Set partial quantities transfered for both products with lots
        Put those quantities in a package

        For the Lot A product, declare a loss

        Check the quantities have been put in a Loss picking
        """
        self.initiate_values()
        self.picking_1.action_assign()

        lines = self.picking_1.move_line_ids
        self.assertEqual(len(lines), 2)

        line_lot_a = lines.filtered(lambda line: line.lot_id == self.product_1_lotA)
        line_lot_b = lines.filtered(lambda line: line.lot_id == self.product_1_lotB)
        line_lot_b.qty_done = 2.0
        line_lot_a.qty_done = 1.0

        self.picking_1._put_in_pack(line_lot_a | line_lot_b)

        # As the original line has been updated with qty_done = 0 and the remaining
        # quantity to transfer in reserved_qty
        line_lot_a.action_loss_quantity()

        done_line = self.picking_1.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA and line.result_package_id
        )

        # Check that the original line has been deleted
        self.assertFalse(line_lot_a.exists())

        # The remaining line on original picking should have the reserved
        # quantity == the done quantity
        self.assertEqual(done_line.reserved_qty, 1.0)  # Original qty == 3.0 - 2.0 loss
        self.assertEqual(done_line.qty_done, 1)

        self.assertEqual(2.0, line_lot_b.reserved_qty)
        self.assertEqual(0.0, line_lot_b.qty_done)

        loss_pickings = self._get_loss_pickings()

        self.assertEqual(1, len(loss_pickings))
        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        self.assertTrue(line)
        self.assertEqual(line.state, "assigned")
        self.assertEqual(line.reserved_uom_qty, 2)

        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )
        self.assertFalse(line)

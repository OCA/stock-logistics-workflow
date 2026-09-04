# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError

from .common import OperationLossQuantityCommon


class TestQuantityLoss(OperationLossQuantityCommon):
    def test_check_is_allowed_config(self):
        self.initiate_values_no_tracking()
        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_2.qty_done = 1.0

        # Unset the Warehouse global config
        self.warehouse.use_loss_picking = False
        with self.assertRaises(UserError):
            line_2.action_lose_quantity()

    def test_check_is_allowed_done(self):
        self.initiate_values_no_tracking()
        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)

        # Transfer the whole picking
        for line in self.picking_2.move_line_ids:
            line.qty_done = line.reserved_uom_qty
        self.picking_2._action_done()
        with self.assertRaises(UserError):
            line_2.action_lose_quantity()

    def test_initiate_values_no_tracking_initial_situation(self):
        self.initiate_values_no_tracking()
        lines = self.picking_2.move_line_ids
        self.assertEqual(len(lines), 2)
        line_p2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_p3 = lines.filtered(lambda line: line.product_id == self.product_3)
        self.assertEqual(line_p2.reserved_uom_qty, 6)
        self.assertEqual(line_p3.reserved_uom_qty, 2)

    def test_loss_line_no_tracking(self):
        self.initiate_values_no_tracking()

        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 1.0

        quants_available_quantity_line_2_before = self._get_quants_available_qty(line_2)

        line_2.action_lose_quantity()

        quants_available_quantity_line_2_after = self._get_quants_available_qty(line_2)

        self.assertEqual(
            quants_available_quantity_line_2_before,
            quants_available_quantity_line_2_after,
        )

        self.assertEqual(line_2.reserved_qty, 1.0)
        self.assertEqual(line_2.qty_done, line_2.reserved_uom_qty)

        loss_pickings = self._get_loss_pickings()

        self.assertEqual(1, len(loss_pickings))
        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.product_id == self.product_3
        )
        self.assertFalse(line)

        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.product_id == self.product_2
        )
        self.assertTrue(line)

        self.assertEqual(line.state, "assigned")
        self.assertEqual(line.reserved_uom_qty, 5)

        # Check activity is generated
        self.assertTrue(loss_pickings.activity_ids)
        self.assertEqual(self.user_demo, loss_pickings.activity_user_id)

        # make an inventory adjustment and check that the loss picking is now
        # cancelled
        self._create_quantities(
            line_2.product_id,
            line_2.reserved_uom_qty,
            location=line_2.location_id,
            lot=line_2.lot_id,
            package=line_2.package_id,
        )
        self.assertEqual(loss_pickings.state, "cancel")

    def test_loss_line_no_tracking_multi(self):
        """
        Declare a loss quantity on both lines - this is not common
        through interface but can be done programmatically
        """
        self.initiate_values_no_tracking()

        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 1.0

        lines.action_lose_quantity()

        for line in lines:
            self.assertEqual(line.reserved_qty, 1.0)
            self.assertEqual(line.qty_done, line.reserved_qty)

        loss_pickings = self._get_loss_pickings()
        self.assertEqual(2, len(loss_pickings))

    def test_loss_line_no_tracking_with_pack(self):
        self.initiate_values_no_tracking()

        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 2.0

        self.picking_2._put_in_pack(line_2 | line_3)
        line_2_pack = self.picking_2.move_line_ids.filtered(
            lambda line: line.result_package_id and line.product_id == self.product_2
        )
        line_3_pack = self.picking_2.move_line_ids.filtered(
            lambda line: line.result_package_id and line.product_id == self.product_3
        )

        # Line 2 does not contain anymore a qty_done after put in pack
        # And a new line with the result package has been created
        self.assertEqual(len(self.picking_2.move_line_ids), 3)
        self.assertNotEqual(line_2, line_2_pack)
        self.assertEqual(line_2.qty_done, 0)
        self.assertEqual(line_2.reserved_qty, 5)
        self.assertEqual(line_3, line_3_pack)

        line_2.action_lose_quantity()

        loss_pickings = self._get_loss_pickings()
        self.assertEqual(1, len(loss_pickings))
        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.product_id == self.product_3
        )
        self.assertFalse(line)

        line = loss_pickings.move_line_ids.filtered(
            lambda line: line.product_id == self.product_2
        )
        self.assertTrue(line)

        self.assertEqual(line.state, "assigned")
        self.assertEqual(line.reserved_uom_qty, 5)

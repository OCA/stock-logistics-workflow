# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests import TransactionCase

from .common import OperationLossQuantityCommon


class TestQuantityLoss(OperationLossQuantityCommon, TransactionCase):
    def test_check_is_allowed_config(self):
        """
        Check the is_action_loss_qty_allowed value and constraint
        """
        self.initiate_values_no_tracking()
        self.picking_2.action_assign()
        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_2.qty_done = 1.0

        # Unset the Warehouse global config
        self.warehouse.use_loss_picking = False
        with self.assertRaises(UserError):
            line_2.action_loss_quantity()

    def test_check_is_allowed_done(self):
        """
        Check the is_action_loss_qty_allowed value and constraint
        """
        self.initiate_values_no_tracking()
        self.picking_2.action_assign()
        lines = self.picking_2.move_line_ids
        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)

        # Transfer the whole picking
        for line in self.picking_2.move_line_ids:
            line.qty_done = line.reserved_uom_qty
        self.picking_2._action_done()
        with self.assertRaises(UserError):
            line_2.action_loss_quantity()

    def test_loss_line_no_tracking(self):
        """Create loss of product_2 without tracking"""
        self.initiate_values_no_tracking()

        self.picking_2.action_assign()

        reserved_quantity = sum(
            [line.reserved_qty for line in self.picking_2.move_line_ids]
        )
        self.assertEqual(reserved_quantity, 4.0)

        lines = self.picking_2.move_line_ids
        self.assertEqual(len(lines), 2)

        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 1.0

        # Do the operation with demo user
        line_2.action_loss_quantity()

        # Check new pack operation
        new_line_2 = self.picking_2.move_line_ids.filtered(
            lambda line: line.product_id == self.product_2
        )
        new_line_3 = self.picking_2.move_line_ids.filtered(
            lambda line: line.product_id == self.product_3
        )
        self.assertNotEqual(line_2, new_line_2)
        self.assertEqual(new_line_2.reserved_qty, 1.0)  # Original qty == 3.0 - 2.0 loss
        self.assertEqual(new_line_2.qty_done, 1)

        # Nothing happened to product 1
        self.assertEqual(line_3, new_line_3)

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
        self.assertEqual(line.reserved_uom_qty, 2)

        # Check activity is generated
        self.assertTrue(loss_pickings.activity_ids)
        self.assertEqual(self.user_demo, loss_pickings.activity_user_id)

    def test_loss_line_no_tracking_multi(self):
        """
        Product 2: 1.0 quantity done (demand 6.0)
        Product 3: 1.0 quantity done (demand 1.0)

        Declare a loss quantity on both lines - this is not common
        through interface but can be done programmatically
        """
        self.initiate_values_no_tracking()

        self.picking_2.action_assign()

        reserved_quantity = sum(
            [line.reserved_qty for line in self.picking_2.move_line_ids]
        )
        self.assertEqual(reserved_quantity, 4.0)

        lines = self.picking_2.move_line_ids
        self.assertEqual(len(lines), 2)

        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 1.0

        # line 3 is done at 100%
        with self.assertRaises(UserError):
            (line_2 | line_3).action_loss_quantity()

        line_2.action_loss_quantity()

        # Check new pack operation
        new_line_2 = self.picking_2.move_line_ids.filtered(
            lambda line: line.product_id == self.product_2
        )
        new_line_3 = self.picking_2.move_line_ids.filtered(
            lambda line: line.product_id == self.product_3
        )
        self.assertNotEqual(line_2, new_line_2)
        self.assertEqual(new_line_2.reserved_qty, 1.0)  # Original qty == 3.0 - 2.0 loss
        self.assertEqual(new_line_2.qty_done, 1)

        # Nothing happened to product 1
        self.assertEqual(line_3, new_line_3)

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
        self.assertEqual(line.reserved_uom_qty, 2)

    def test_loss_line_no_tracking_with_pack(self):
        """Create loss of product_2 without tracking"""
        self.initiate_values_no_tracking()

        self.picking_2.action_assign()

        reserved_quantity = sum(
            [line.reserved_qty for line in self.picking_2.move_line_ids]
        )
        self.assertEqual(reserved_quantity, 4.0)

        lines = self.picking_2.move_line_ids
        self.assertEqual(len(lines), 2)

        line_2 = lines.filtered(lambda line: line.product_id == self.product_2)
        line_3 = lines.filtered(lambda line: line.product_id == self.product_3)
        line_2.qty_done = 1.0
        line_3.qty_done = 1.0
        self.picking_2._put_in_pack(line_2 | line_3)

        # Line 2 does not contain anymore a qty_done after put in pack
        # And a new line with the result package has been created
        packed_line_2 = self.picking_2.move_line_ids.filtered(
            lambda line: line.result_package_id and line.product_id == self.product_2
        )

        line_2.action_loss_quantity()
        loss_pickings = self._get_loss_pickings()

        # Check new pack operation
        new_line_3 = self.picking_2.move_line_ids.filtered(
            lambda line: line.product_id == self.product_3
            and not line.result_package_id
        )
        self.assertNotEqual(line_2, packed_line_2)
        self.assertEqual(
            packed_line_2.reserved_qty, 1.0
        )  # Original qty == 3.0 - 2.0 loss
        self.assertEqual(packed_line_2.qty_done, 1)

        # Nothing happened to product 1
        self.assertTrue(line_3)
        self.assertFalse(new_line_3)

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
        self.assertEqual(line.reserved_uom_qty, 2)

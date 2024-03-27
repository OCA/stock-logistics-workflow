# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockMoveLineLockQtyDone(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.assigned_picking = cls.env["stock.picking"].search(
            [("state", "=", "assigned")], limit=1
        )
        cls.move_line = cls.assigned_picking.move_line_ids[0]

    def test_0(self):
        self.assertEqual(self.assigned_picking.state, "assigned")
        self.move_line.qty_done = 1
        self.assigned_picking.action_set_quantities_to_reservation()
        self.assigned_picking._action_done()
        self.assertEqual(self.assigned_picking.state, "done")
        with self.assertRaises(
            UserError,
            msg="This move is locked, you can't edit the done quantity unless you "
            "unlock it",
        ):
            self.move_line.qty_done = 0
        self.assigned_picking.action_toggle_is_locked()
        with self.assertRaises(
            UserError,
            msg="You are not allowed to change the quantity done for done moves",
        ):
            self.move_line.qty_done = 0
        self.env.user.groups_id += self.env.ref(
            "stock_move_line_lock_qty_done.group_stock_move_can_edit_done_qty"
        )
        self.move_line.qty_done = 0
        self.assertEqual(self.move_line.qty_done, 0)

# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import TestCommon


@tagged("post_install", "-at_install")
class TestMoveLine(TestCommon):
    def test_move_line_onchange_future_date_raises(self):
        """Setting a future date_backdating on a move line raises UserError."""
        future_date = self._get_datetime_backdating(-1)
        move_line = self.picking.move_line_ids[:1]
        move_line.date_backdating = future_date
        with self.assertRaises(UserError):
            move_line.onchange_date_backdating()

    def test_move_line_onchange_past_date_ok(self):
        """A past date_backdating passes the onchange check."""
        past_date = self._get_datetime_backdating(1)
        move_line = self.picking.move_line_ids[:1]
        move_line.date_backdating = past_date
        # Should not raise
        move_line.onchange_date_backdating()
        self.assertEqual(move_line.date_backdating, past_date)

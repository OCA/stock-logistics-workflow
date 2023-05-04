# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2023 FactorLibre - Boris Alias
from odoo.tests.common import TransactionCase


class TestMove(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_compute_has_move_lines(self):
        move_with_lines = self.env["stock.move"].search(
            [("move_line_ids", "!=", False)], limit=1
        )

        move_without_lines = self.env["stock.move"].search(
            [("move_line_ids", "=", False)], limit=1
        )

        self.assertEqual(move_with_lines.has_move_lines, True)
        self.assertEqual(move_without_lines.has_move_lines, False)

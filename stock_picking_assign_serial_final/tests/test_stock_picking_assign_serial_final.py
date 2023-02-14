# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase

from .common import CommonStockPickingAssignSerialFinal


class TestStockPickingAutoCreateLot(
    CommonStockPickingAssignSerialFinal, TransactionCase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls._create_product()
        cls.product_serial = cls._create_product(tracking="serial")
        cls._create_picking()
        cls._create_move(product=cls.product_serial, qty=5.0)

    def test_wizard_assign_serial_final(self):
        self.picking.action_assign()
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        wiz = (
            self.env["stock.assign.serial"]
            .with_context(
                default_product_id=move.product_id.id,
                default_move_id=move.id,
                default_next_serial_number="XZ000001MTR",
            )
            .create({})
        )
        self.assertEqual(wiz.next_serial_count, 5)
        wiz.final_serial_number = "XZ000007MTR"
        self.assertEqual(wiz.next_serial_count, 7)

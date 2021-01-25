# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase

from .common import CommonStockPickingAutoCreateLot


class TestStockPickingAutoCreateLot(CommonStockPickingAutoCreateLot, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create 3 products with lot/serial and auto_create True/False
        cls.product = cls._create_product()
        cls.product_serial = cls._create_product(tracking="serial")
        cls.product_serial_not_auto = cls._create_product(tracking="serial", auto=False)
        cls.picking_type_in.auto_create_lot = True

        cls._create_picking()
        cls._create_move(product=cls.product, qty=2.0)
        cls._create_move(product=cls.product_serial, qty=3.0)
        cls._create_move(product=cls.product_serial_not_auto, qty=4.0)

        cls.picking.action_assign()

    def test_manual_lot(self):

        # Check the display field
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(move.display_assign_serial)

        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertTrue(move.display_assign_serial)

        # Assign manual serials
        for line in move.move_line_ids:
            line.lot_id = self.lot_obj.create(line._prepare_auto_lot_values())

        self.picking.button_validate()
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)

    def test_auto_create_lot(self):
        # Check the display field
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(move.display_assign_serial)

        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertTrue(move.display_assign_serial)

        self.picking.action_done()
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)

    def test_auto_create_transfer_lot(self):
        # Check the display field
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(move.display_assign_serial)

        moves = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_id)

        self.picking.button_validate()
        for line in moves.mapped("move_line_ids"):
            self.assertTrue(line.lot_id)

        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)

# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase

from .common import CommonStockPickingAutoCreateLot


class TestStockPickingAutoCreateLot(CommonStockPickingAutoCreateLot, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create 3 products with lot/serial and auto_create True/False
        cls.product = cls._create_product()
        cls.product_serial = cls._create_product(tracking="serial")
        cls.product_serial_not_auto = cls._create_product(tracking="serial", auto=False)
        cls.picking_type_in.auto_create_lot = True

        cls.picking = cls._create_picking()
        cls._create_move(product=cls.product, qty=2.0)
        cls._create_move(product=cls.product_serial, qty=3.0)
        cls._create_move(product=cls.product_serial_not_auto, qty=4.0)

    def test_manual_lot(self):
        self.picking.action_assign()
        # Check the display field
        move = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(move.display_assign_serial)

        move = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertTrue(move.display_assign_serial)

        # Assign manual serials
        for line in move.move_line_ids:
            line.lot_id = self.lot_obj.create(line._prepare_auto_lot_values())

        self.picking.button_validate()
        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)

    def test_auto_create_lot(self):
        self.picking.action_assign()
        # Check the display field
        move = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(move.display_assign_serial)

        move = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertTrue(move.display_assign_serial)

        self.picking._action_done()
        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)
        lot = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial_not_auto.id)]
        )
        self.assertFalse(lot)

    def test_auto_create_lot_for_all_products(self):
        self.picking_type_in.auto_create_lot_for_all_products = True
        self.product.auto_create_lot = False
        self.picking.action_assign()
        # Check the display field
        move = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(move.display_assign_serial)

        move = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertFalse(move.display_assign_serial)

        self.picking._action_done()
        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial_not_auto.id)]
        )
        self.assertEqual(len(lot), 4)

    def test_auto_create_transfer_lot(self):
        self.picking.action_assign()
        moves = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_id)

        # Test the exception if manual serials are not filled in
        with self.assertRaises(UserError), self.cr.savepoint():
            self.picking.button_validate()

        # Assign manual serial for product that need it
        moves = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )

        # Assign manual serials
        for line in moves.mapped("move_line_ids"):
            line.lot_id = self.lot_obj.create(line._prepare_auto_lot_values())

        self.picking.button_validate()
        for line in moves.mapped("move_line_ids"):
            self.assertTrue(line.lot_id)

        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)

        # Check if lots are unique per move and per product if managed
        # per serial
        move_lines_serial = self.picking.move_line_ids.filtered(
            lambda m: m.product_id.tracking == "serial" and m.product_id.auto_create_lot
        )
        serials = []
        for move in move_lines_serial:
            serials.append(move.lot_id.name)
        self.assertUniqueIn(serials)

    def test_multi_auto_create_lot(self):
        """
        Create two pickings
        Try to validate them together
        Check if lots have been assigned to each move
        """
        self.picking.action_assign()
        picking_1 = self.picking
        picking_2 = self._create_picking()
        self._create_move(product=self.product_serial, qty=3.0, picking=picking_2)
        picking_2.action_assign()
        pickings = picking_1 | picking_2

        moves = pickings.mapped("move_ids").filtered(
            lambda m: m.product_id == self.product_serial
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_id)

        pickings._action_done()
        for line in moves.mapped("move_line_ids"):
            self.assertTrue(line.lot_id)

        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 6)

    @freeze_time("2023-03-21")
    def test_lot_name_expression(self):
        self.picking_type_in.auto_create_lot_name_expression = (
            "{{stock_move_line.picking_id.partner_id.name}}/"
            "{{datetime.date.today().isoformat()}}"
        )
        self.picking.action_assign()
        self.picking._action_done()
        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)
        self.assertEqual(lot.name, "Supplier - test/2023-03-21")
        # products with serial tracking should not use the expression
        serials = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(serials), 3)
        self.assertRegex(serials[0].name, r"^\d+$")
        self.assertNotEqual(serials[0].name, serials[1].name)

    def test_not_reuse_existing_lot(self):
        # self.picking_type_in.use_existing_lots is False by default
        self.picking_type_in.auto_create_lot_name_expression = "test lot"
        self.env["stock.lot"].create(
            {
                "name": "test lot",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        self.picking.action_assign()
        with self.assertRaises(ValidationError):
            self.picking._action_done()

    def test_reuse_existing_lot(self):
        self.picking_type_in.use_existing_lots = True
        self.picking_type_in.auto_create_lot_name_expression = "test lot"
        self.env["stock.lot"].create(
            {
                "name": "test lot",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        self.picking.action_assign()
        self.picking._action_done()
        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)

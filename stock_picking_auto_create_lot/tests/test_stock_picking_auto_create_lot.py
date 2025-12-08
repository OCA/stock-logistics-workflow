# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
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

        cls._create_picking()
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
        self._assign_manual_serials(move)
        self.picking.move_ids.picked = True
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
        # Assign manual serials
        self._assign_manual_serials(move)
        self.picking.move_ids.picked = True

        self.picking._action_done()
        lot = self.env["stock.lot"].search([("product_id", "=", self.product.id)])
        self.assertEqual(len(lot), 1)
        # Search for serials
        lot = self.env["stock.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3)

    def test_auto_create_transfer_lot(self):
        self.picking.action_assign()
        moves = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_name)

        # Test the exception if manual serials are not filled in
        with self.assertRaises(UserError), self.cr.savepoint():
            self.picking.button_validate()

        # Assign manual serial for product that need it
        moves = self.picking.move_ids.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        # Assign manual serials
        self._assign_manual_serials(moves)
        self.picking.move_ids.picked = True

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
        self._create_picking()
        picking_2 = self.picking
        self._create_move(product=self.product_serial, qty=3.0)
        picking_2.action_assign()
        pickings = picking_1 | picking_2

        moves = pickings.mapped("move_ids").filtered(
            lambda m: m.product_id == self.product_serial
            and m.product_id.auto_create_lot
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_name)

        pickings._action_done()
        for line in moves.mapped("move_line_ids"):
            self.assertTrue(line.lot_name)

    def test_immediate_validate_tracked_move_with_auto_create_lot(self):
        # Clear existing move if not the picking will open backorder wizard because
        # when we manually assign lot for serial_not_auto product, other products still
        # have 0 done qty.
        self.picking.move_ids = False
        self._create_move(product=self.product_serial, qty=4.0)
        self.picking.action_assign()
        self.picking.button_validate()
        # Confirm that validation is not blocked, for example, by create-backorder
        # wizard.
        self.assertEqual(self.picking.state, "done")

    def test_multiple_sml_for_one_stock_move(self):
        """
        Create a picking and we receive goods from supplier with different features so
        we want different lots by each stock move line.
        """
        self._create_picking()
        self._create_move(product=self.product, qty=50.0)
        self.picking.action_assign()
        self.picking.move_line_ids.quantity = 25.0
        # new sml with 25.0 units
        self.picking.move_line_ids.copy({"quantity": 25.0})
        self.picking.button_validate()
        lots = self.picking.move_line_ids.lot_id
        self.assertEqual(len(lots), 2)

    def _assign_manual_serials(self, moves):
        # Assign manual serials
        moves.picking_id._set_auto_lot()
        moves.move_line_ids.quantity = 1.0
        for line in moves.move_line_ids:
            line.lot_name = self.env["ir.sequence"].next_by_code("stock.lot.serial")

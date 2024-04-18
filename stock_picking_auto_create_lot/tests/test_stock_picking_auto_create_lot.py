# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
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

        cls.product_2 = cls._create_product()

        cls._create_picking()
        cls._create_move(product=cls.product, qty=2.0)
        cls._create_move(product=cls.product_serial, qty=3.0)
        cls._create_move(product=cls.product_serial_not_auto, qty=4.0)

    def test_manual_lot(self):
        self.picking.action_assign()
        # Check the display field
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(
            move.display_assign_serial, msg="Serial numbers must be not assigned"
        )

        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertTrue(
            move.display_assign_serial, msg="Serial numbers must be assigned"
        )

        # Assign manual serials
        for line in move.move_line_ids:
            line.lot_id = self.lot_obj.create(line._prepare_auto_lot_values())

        self.picking.button_validate()
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1, msg="Must be equal 1 lot")
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3, msg="Must be equal 3 lots")

    def test_auto_create_lot(self):
        self.picking.action_assign()
        # Check the display field
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(
            move.display_assign_serial, msg="Serial numbers must be not assigned"
        )

        move = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertTrue(
            move.display_assign_serial, msg="Serial numbers must be assigned"
        )

        self.picking._action_done()
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1, msg="Must be equal 1 lot")
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3, msg="Must be equal 3 lots")

    def test_auto_create_transfer_lot(self):
        self.picking.action_assign()
        moves = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_id, msg="The lot should not be assigned")

        # Test the exception if manual serials are not filled in
        with self.assertRaises(UserError), self.cr.savepoint():
            self.picking.button_validate()

        # Assign manual serial for product that need it
        moves = self.picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )

        # Assign manual serials
        for line in moves.mapped("move_line_ids"):
            line.lot_id = self.lot_obj.create(line._prepare_auto_lot_values())

        self.picking.button_validate()
        for line in moves.mapped("move_line_ids"):
            self.assertTrue(line.lot_id, msg="The lot should be assigned")

        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1, msg="Must be equal 1 lot")
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 3, msg="Must be equal 3 lots")

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

        moves = pickings.mapped("move_lines").filtered(
            lambda m: m.product_id == self.product_serial
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_id, msg="The lot should not be assigned")

        pickings._action_done()
        for line in moves.mapped("move_line_ids"):
            self.assertTrue(line.lot_id, msg="The lot should be assigned")

        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertEqual(len(lot), 1, msg="Must be 1 lot")
        # Search for serials
        lot = self.env["stock.production.lot"].search(
            [("product_id", "=", self.product_serial.id)]
        )
        self.assertEqual(len(lot), 6, msg="Must be 6 lots")

    def test_auto_create_lot_2(self):
        """Test check create lots per product"""
        picking = (
            self.env["stock.picking"]
            .with_context(default_picking_type_id=self.picking_type_in.id)
            .create(
                {
                    "partner_id": self.supplier.id,
                    "picking_type_id": self.picking_type_in.id,
                    "location_id": self.supplier_location.id,
                }
            )
        )
        location_dest = picking.picking_type_id.default_location_dest_id
        self.env["stock.move"].create(
            [
                {
                    "name": "test-{product}".format(product=self.product.name),
                    "product_id": self.product.id,
                    "picking_id": picking.id,
                    "picking_type_id": picking.picking_type_id.id,
                    "product_uom_qty": 5,
                    "product_uom": self.product.uom_id.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": location_dest.id,
                },
                {
                    "name": "test-{product}".format(product=self.product_2.name),
                    "product_id": self.product_2.id,
                    "picking_id": picking.id,
                    "picking_type_id": picking.picking_type_id.id,
                    "product_uom_qty": 7,
                    "product_uom": self.product_2.uom_id.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": location_dest.id,
                },
            ]
        )
        picking.action_assign()
        # Check the display field
        move = picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial
        )
        self.assertFalse(
            move.display_assign_serial, msg="Serial numbers must be not assigned"
        )

        move = picking.move_lines.filtered(
            lambda m: m.product_id == self.product_serial_not_auto
        )
        self.assertFalse(
            move.display_assign_serial, msg="Serial numbers must be not assigned"
        )
        move_lines = picking.move_line_ids.filtered(
            lambda m: m.product_id == self.product or m.product_id == self.product_2
        )
        picking._action_done()
        lots = self.env["stock.production.lot"].search(
            [("product_id", "in", [self.product.id, self.product_2.id])]
        )
        self.assertEqual(len(lots), 2, msg="Must be equal to 2")
        self.assertUniqueIn(move_lines.mapped("lot_id.name"))

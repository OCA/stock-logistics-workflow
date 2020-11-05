# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase

from .common import CommonStockPickingAutoCreateLot


class TestStockPickingAutoCreateLot(CommonStockPickingAutoCreateLot, SavepointCase):
    def test_auto_create_lot(self):
        # Create 3 products with lot/serial and auto_create True/False
        self.product = self._create_product()
        self.product_serial = self._create_product(tracking="serial")
        self.product_serial_not_auto = self._create_product(
            tracking="serial", auto=False
        )
        self.picking_type_in.auto_create_lot = True

        self._create_picking()
        self._create_move(product=self.product, qty=2.0)
        self._create_move(product=self.product_serial, qty=3.0)
        self._create_move(product=self.product_serial_not_auto, qty=4.0)

        self.picking.action_assign()
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

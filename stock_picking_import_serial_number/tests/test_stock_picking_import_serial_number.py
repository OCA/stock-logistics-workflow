# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import SavepointCase

from .common import CommonStockPickingImportSerial


class TestStockPickingImportSN(CommonStockPickingImportSerial, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create 3 products with lot/serial and auto_create True/False
        cls.product_lot = cls._create_product()
        cls.product_serial = cls._create_product(tracking="serial", reference="1234")
        cls.product_no_tracking = cls._create_product(tracking="none")

        cls.picking_in_01 = cls._create_picking()
        cls._create_move(picking=cls.picking_in_01, product=cls.product_lot, qty=2.0)
        cls._create_move(picking=cls.picking_in_01, product=cls.product_serial, qty=3.0)
        cls._create_move(
            picking=cls.picking_in_01, product=cls.product_no_tracking, qty=4.0
        )

        cls.picking_in_01.action_assign()

        cls.picking_in_02 = cls._create_picking()
        cls._create_move(picking=cls.picking_in_02, product=cls.product_lot, qty=2.0)
        cls._create_move(picking=cls.picking_in_02, product=cls.product_serial, qty=3.0)
        cls._create_move(
            picking=cls.picking_in_02, product=cls.product_no_tracking, qty=4.0
        )
        cls.picking_in_02.action_assign()

    def _create_wizard(self, pickings=False):
        if not pickings:
            pickings = self.picking_in_01 | self.picking_in_02
        return self.env["stock.picking.import.serial.number.wiz"].create(
            {
                "picking_ids": [(6, 0, pickings.ids)],
                "data_file": self.file,
                "filename": "SNImport.xls",
            }
        )

    def test_import_serial_number_no_file(self):
        wiz = self._create_wizard()
        wiz.data_file = False
        with self.assertRaises(UserError):
            wiz.action_import()

    def test_import_serial_number_no_create_lot(self):
        self.picking_type_in.use_create_lots = False
        wiz = self._create_wizard()
        with self.assertRaises(UserError):
            wiz.action_import()

    def test_import_serial_number(self):
        wiz = self._create_wizard()
        wiz.action_import()
        smls = self.picking_in_01.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)
        smls = self.picking_in_02.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)

    def test_import_serial_number_no_show_reserved(self):
        self.picking_in_01.picking_type_id.show_reserved = False
        picking = self.picking_in_01.copy()
        picking.action_confirm()
        picking.action_assign()
        wiz = self._create_wizard(pickings=picking)
        wiz.action_import()
        smls = picking.move_line_nosuggest_ids.filtered("lot_name")
        self.assertEqual(len(smls), 6)

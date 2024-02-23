# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon

from .common import CommonStockPickingImportSerial


class TestStockPickingImportSN(CommonStockPickingImportSerial, BaseCommon):
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

    def _create_wizard(self, pickings=False, filename=False):
        filename = filename if filename else "SNImport-1.xls"
        if not pickings:
            pickings = self.picking_in_01 | self.picking_in_02
        wizard_form = Form(
            self.env["stock.picking.import.serial.number.wiz"].with_context(
                default_picking_ids=pickings.ids,
                default_filename=filename,
            )
        )
        wizard_form.data_file = self._data_file("data/%s" % filename)
        return wizard_form.save()

    @mute_logger("odoo.models.unlink")
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

    @mute_logger("odoo.models.unlink")
    def test_import_serial_number_01(self):
        # Full import: Lots + packages (SNImport-1.xls)
        wiz = self._create_wizard()
        wiz.action_import()
        smls = self.picking_in_01.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        package_names = smls.mapped("result_package_id.name")
        self.assertIn("PACK-1", package_names)
        self.assertIn("PACK-2", package_names)
        self.assertIn("PACK-3", package_names)
        smls = self.picking_in_02.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        package_names = smls.mapped("result_package_id.name")
        self.assertIn("PACK-1", package_names)
        self.assertIn("PACK-2", package_names)
        self.assertIn("PACK-3", package_names)

    @mute_logger("odoo.models.unlink")
    def test_import_serial_number_02(self):
        # Full import: Lots + packages (SNImport-2.xls)
        wiz = self._create_wizard(filename="SNImport-2.xls")
        wiz.action_import()
        smls = self.picking_in_01.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        package_names = smls.mapped("result_package_id.name")
        self.assertIn("PACK-1", package_names)
        self.assertNotIn("PACK-2", package_names)
        self.assertNotIn("PACK-3", package_names)
        smls = self.picking_in_02.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        package_names = smls.mapped("result_package_id.name")
        self.assertIn("PACK-1", package_names)
        self.assertNotIn("PACK-2", package_names)
        self.assertNotIn("PACK-3", package_names)

    @mute_logger("odoo.models.unlink")
    def test_import_serial_number_03(self):
        # Import only lots
        wiz = self._create_wizard()
        wiz.sn_package_column_index = 10
        wiz.action_import()
        smls = self.picking_in_01.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        self.assertFalse(smls[0].result_package_id)
        smls = self.picking_in_02.move_line_ids.filtered("lot_name")
        self.assertEqual(len(smls), 3)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        self.assertFalse(smls[0].result_package_id)

    @mute_logger("odoo.models.unlink")
    def test_import_serial_number_no_show_reserved_01(self):
        # Full import: Lots + packages (SNImport-1.xls)
        self.picking_in_01.picking_type_id.show_reserved = False
        picking = self.picking_in_01.copy()
        picking.action_confirm()
        picking.action_assign()
        wiz = self._create_wizard(pickings=picking)
        wiz.action_import()
        smls = picking.move_line_nosuggest_ids.filtered("lot_name")
        self.assertEqual(len(smls), 6)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        self.assertIn("LOT-4", lot_names)
        self.assertIn("LOT-5", lot_names)
        self.assertIn("LOT-6", lot_names)
        package_names = smls.mapped("result_package_id.name")
        self.assertIn("PACK-1", package_names)
        self.assertIn("PACK-2", package_names)
        self.assertIn("PACK-3", package_names)
        self.assertIn("PACK-4", package_names)
        self.assertIn("PACK-5", package_names)
        self.assertIn("PACK-6", package_names)

    @mute_logger("odoo.models.unlink")
    def test_import_serial_number_no_show_reserved_02(self):
        # Full import: Lots + packages (SNImport-2.xls)
        self.picking_in_01.picking_type_id.show_reserved = False
        picking = self.picking_in_01.copy()
        picking.action_confirm()
        picking.action_assign()
        wiz = self._create_wizard(pickings=picking, filename="SNImport-2.xls")
        wiz.action_import()
        smls = picking.move_line_nosuggest_ids.filtered("lot_name")
        self.assertEqual(len(smls), 6)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        self.assertIn("LOT-4", lot_names)
        self.assertIn("LOT-5", lot_names)
        self.assertIn("LOT-6", lot_names)
        package_names = smls.mapped("result_package_id.name")
        self.assertIn("PACK-1", package_names)
        self.assertIn("PACK-2", package_names)
        self.assertNotIn("PACK-3", package_names)
        self.assertNotIn("PACK-4", package_names)
        self.assertNotIn("PACK-5", package_names)
        self.assertNotIn("PACK-6", package_names)

    @mute_logger("odoo.models.unlink")
    def test_import_serial_number_no_show_reserved_03(self):
        # Import only lots
        self.picking_in_01.picking_type_id.show_reserved = False
        picking = self.picking_in_01.copy()
        picking.action_confirm()
        picking.action_assign()
        wiz = self._create_wizard(pickings=picking)
        wiz.sn_package_column_index = 10
        wiz.action_import()
        smls = picking.move_line_nosuggest_ids.filtered("lot_name")
        self.assertEqual(len(smls), 6)
        lot_names = smls.mapped("lot_name")
        self.assertIn("LOT-1", lot_names)
        self.assertIn("LOT-2", lot_names)
        self.assertIn("LOT-3", lot_names)
        self.assertIn("LOT-4", lot_names)
        self.assertIn("LOT-5", lot_names)
        self.assertIn("LOT-6", lot_names)
        self.assertFalse(smls[0].result_package_id)

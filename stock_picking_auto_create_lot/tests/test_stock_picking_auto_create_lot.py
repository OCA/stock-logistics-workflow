# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

from ..models.res_config_settings import CONFIG_PARAM_SKU_TRAILING
from .common import CommonStockPickingAutoCreateLot


@tagged("test1")
class TestStockPickingAutoCreateLot(CommonStockPickingAutoCreateLot, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create 3 products with lot/serial and auto_create True/False
        cls.product = cls._create_product(option="odoo_sequence")
        cls.product_serial = cls._create_product(
            tracking="serial", option="odoo_sequence"
        )
        cls.product_serial_not_auto = cls._create_product(
            tracking="serial", option=False
        )
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
            lambda m: m.product_id.tracking == "serial"
            and m.product_id.product_tmpl_id.auto_create_lot_option
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
            and m.product_id.product_tmpl_id.auto_create_lot_option
        )
        for line in moves.mapped("move_line_ids"):
            self.assertFalse(line.lot_name)

        pickings._action_done()
        for line in moves.mapped("move_line_ids"):
            self.assertTrue(line.lot_name)

    def test_sku_based_generates_incremental_serials(self):
        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_8888"
        )
        self._create_picking()
        self._create_move(product=product, qty=2.0)
        self.picking_type_in.auto_create_lot = True

        self.picking.action_assign()

        # Ensure 2 move lines exist for serial tracking
        smls = self.picking.move_line_ids.filtered(
            lambda line: line.product_id == product
        )
        self.assertEqual(len(smls), 2)

        self.picking.button_validate()

        lots = self.env["stock.lot"].search([("product_id", "=", product.id)])
        names = sorted(lots.mapped("name"))
        self.assertEqual(names, ["FURN_8888-1", "FURN_8888-2"])

    def test_sku_based_multi_picking_validate_unique(self):
        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_7777"
        )
        self.picking_type_in.auto_create_lot = True

        self._create_picking()
        picking_1 = self.picking
        self._create_move(product=product, qty=1.0)
        picking_1.action_assign()

        self._create_picking()
        picking_2 = self.picking
        self._create_move(product=product, qty=1.0)
        picking_2.action_assign()

        pickings = picking_1 | picking_2
        pickings.button_validate()

        lots = self.env["stock.lot"].search([("product_id", "=", product.id)])
        self.assertEqual(len(lots), 2)
        self.assertUniqueIn(lots.mapped("name"))

    def test_sku_based_without_sku_falls_back_to_odoo_sequence(self):
        product = self._create_product(tracking="serial", option="sku_based", sku=None)
        self.picking_type_in.auto_create_lot = True

        self._create_picking()
        self._create_move(product=product, qty=1.0)
        self.picking.action_assign()

        self.picking.button_validate()

        lot = self.env["stock.lot"].search([("product_id", "=", product.id)], limit=1)
        self.assertTrue(lot)
        # We can't assert exact sequence format, but must be non-empty and not like "-1"
        self.assertTrue(lot.name)
        self.assertFalse(lot.name.startswith("-"))

    def test_sku_based_respects_global_lots_company_null(self):
        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_9999"
        )
        self.picking_type_in.auto_create_lot = True

        # Create global lot (company_id is False)
        global_lot = self.env["stock.lot"].create(
            {
                "name": "FURN_9999-1",
                "product_id": product.id,
                "company_id": False,
            }
        )

        self._create_picking()
        self._create_move(product=product, qty=1.0)
        self.picking.action_assign()
        self.picking.button_validate()

        sml = self.picking.move_line_ids.filtered(
            lambda line: line.product_id == product
        )
        self.assertEqual(len(sml), 1)
        self.assertEqual(sml.lot_id, global_lot)

        lots = self.env["stock.lot"].search([("product_id", "=", product.id)])
        self.assertEqual(len(lots), 1)
        self.assertEqual(lots, global_lot)

    def test_sku_based_trailing_zeroes(self):
        self.env["ir.config_parameter"].sudo().set_param(CONFIG_PARAM_SKU_TRAILING, "3")
        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_1234"
        )

        self.picking_type_in.auto_create_lot = True
        self._create_picking()
        self._create_move(product=product, qty=2.0)
        self.picking.action_assign()
        self.picking.button_validate()

        lots = self.env["stock.lot"].search([("product_id", "=", product.id)])
        self.assertIn("FURN_1234-001", lots.mapped("name"))
        self.assertIn("FURN_1234-002", lots.mapped("name"))

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

    def test_sku_based_missing_sequence_falls_back_to_odoo_sequence(self):
        """If per-product sequence is missing, it must fallback to stock.lot.serial."""
        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_MISS"
        )

        seq = product.auto_create_lot_sequence_id
        self.assertTrue(seq)

        # Make sequence missing without triggering sync hooks.
        seq.sudo().unlink()
        product.write({"auto_create_lot_sequence_id": False})
        self.assertFalse(product.auto_create_lot_sequence_id)

        self._create_picking()
        self._create_move(product=product, qty=1.0)
        self.picking.action_assign()

        sml = self.picking.move_line_ids.filtered(
            lambda line: line.product_id == product
        )[:1]
        self.assertTrue(sml)

        name = sml._get_lot_sequence()
        self.assertTrue(name)
        self.assertFalse(name.startswith("FURN_MISS-"))

    def test_trailing_invalid_or_negative_config_defaults_to_zero(self):
        """Invalid/negative trailing in config param must result in padding=0."""
        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_TRL"
        )
        product.auto_create_lot_sequence_id.write({"padding": 7})
        product.write({"auto_create_lot_sequence_id": False})

        # ValueError branch
        self.env["ir.config_parameter"].sudo().set_param(
            CONFIG_PARAM_SKU_TRAILING, "abc"
        )
        product._auto_lot_sequence_sync_if_needed()
        self.assertEqual(product.auto_create_lot_sequence_id.padding, 0)

        # max(trailing, 0) branch
        product.write({"auto_create_lot_sequence_id": False})
        self.env["ir.config_parameter"].sudo().set_param(
            CONFIG_PARAM_SKU_TRAILING, "-5"
        )
        product._auto_lot_sequence_sync_if_needed()
        self.assertEqual(product.auto_create_lot_sequence_id.padding, 0)

    def test_product_write_syncs_sequence_on_sku_or_company_change(self):
        """Changing SKU/company must sync per-product
        sequence (prefix/padding/company)."""
        self.env["ir.config_parameter"].sudo().set_param(CONFIG_PARAM_SKU_TRAILING, "2")

        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_2000"
        )
        seq = product.auto_create_lot_sequence_id
        self.assertTrue(seq)

        # Put sequence out-of-sync so vals-diff/write path is executed.
        seq.write({"prefix": "BAD-", "padding": 0, "company_id": False})

        company2 = self.env["res.company"].create({"name": "Company 2"})
        product = product.with_context(
            allowed_company_ids=[self.env.company.id, company2.id]
        )

        # Covers: product.product.write hook and sync updates
        product.write({"default_code": "FURN_2001", "company_id": company2.id})

        seq = product.auto_create_lot_sequence_id
        self.assertEqual(seq.prefix, "FURN_2001-")
        self.assertEqual(seq.padding, 2)
        self.assertEqual(seq.company_id, company2)

    def test_product_unlink_deletes_dedicated_sequence(self):
        """Deleting product must delete its dedicated sequence."""
        product = self._create_product(
            tracking="serial", option="sku_based", sku="FURN_DEL"
        )
        seq = product.auto_create_lot_sequence_id
        self.assertTrue(seq)

        seq_id = seq.id
        product.unlink()

        self.assertFalse(self.env["ir.sequence"].browse(seq_id).exists())

    def test_template_write_triggers_sequence_creation_on_option_change(self):
        """Changing template option to sku_based must create sequence for variants."""
        product = self._create_product(
            tracking="serial", option="odoo_sequence", sku="FURN_TPL"
        )
        self.assertFalse(product.auto_create_lot_sequence_id)

        product.product_tmpl_id.write({"auto_create_lot_option": "sku_based"})

        self.assertTrue(product.auto_create_lot_sequence_id)
        self.assertTrue(
            product.auto_create_lot_sequence_id.prefix.startswith("FURN_TPL-")
        )

    def test_settings_trailing_negative_raises_validation_error(self):
        """res.config.settings must not accept negative trailing."""
        with self.assertRaises(ValidationError):
            self.env["res.config.settings"].create({"sku_based_numbers_trailing": -1})

    def _assign_manual_serials(self, moves):
        # Assign manual serials
        moves.picking_id._set_auto_lot()
        moves.move_line_ids.quantity = 1.0
        for line in moves.move_line_ids:
            line.lot_name = self.env["ir.sequence"].next_by_code("stock.lot.serial")

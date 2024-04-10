# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError, ValidationError

from .common import CommonStockPicking


class TestStockPickingAutoCreateLotQty(CommonStockPicking):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a new product and set the following properties:
        # * Create lot every 5 units
        # * Only multiples allowed = True
        cls.product_serial_auto_qty_5_multiples_allowed_true = cls._create_product(
            tracking="lot", auto=True, every_n=5, multiple_allow=True
        )
        # * Only multiples allowed = False
        cls.product_serial_auto_qty_5_multiples_allowed_false = cls._create_product(
            tracking="lot", auto=True, every_n=5, multiple_allow=False
        )
        cls.picking_type_in.auto_create_lot = True
        cls.picking_type_in_2.auto_create_lot = True
        # * tracking "lot" to "none"
        cls.product_no_tracking = cls._create_product(
            tracking="lot", auto=True, every_n=5, multiple_allow=False
        )
        # * tracking every_n = 0
        cls.product_0_every_n = cls._create_product(
            tracking="lot", auto=True, every_n=0, multiple_allow=False
        )

    def test_multiples_allowed_false(self):
        """
        Test that the serial number is created if the quantity
        received is not a multiple of the selected value
        """
        self._create_picking()
        self._create_move(
            product=self.product_serial_auto_qty_5_multiples_allowed_false, qty=8.0
        )
        self.picking.button_validate()
        # Check the display field
        move = self.picking.move_ids.filtered(
            lambda m: m.product_id
            == self.product_serial_auto_qty_5_multiples_allowed_false
        )
        self.assertFalse(
            move.display_assign_serial, msg="Do not display the assigned serial number"
        )

        # Search for serials
        lot = self.lot_obj.search(
            [
                (
                    "product_id",
                    "=",
                    self.product_serial_auto_qty_5_multiples_allowed_false.id,
                )
            ]
        )
        self.assertEqual(
            len(lot), 2, msg="The number of created lots should be equal to 2"
        )

    def test_multiples_allowed_true_1(self):
        """Test that the serial number is not  created if the quantity received
        is a multiple of the selected value"""
        self._create_picking()
        self._create_move(
            product=self.product_serial_auto_qty_5_multiples_allowed_true, qty=8.0
        )
        # check for error
        # reminder = 3>0
        self.assertRaises(UserError, self.picking.button_validate)

    def test_multiples_allowed_true_2(self):
        """Test that the serial number is  created if the quantity received
        is a multiple of the selected value"""
        self._create_picking()
        self._create_move(
            product=self.product_serial_auto_qty_5_multiples_allowed_true, qty=15.0
        )
        self.picking.button_validate()
        # Check the display field
        move = self.picking.move_ids.filtered(
            lambda m: m.product_id
            == self.product_serial_auto_qty_5_multiples_allowed_true
        )
        self.assertFalse(
            move.display_assign_serial, msg="Do not display the assigned serial number"
        )

        # Search for serials
        lot = self.lot_obj.search(
            [
                (
                    "product_id",
                    "=",
                    self.product_serial_auto_qty_5_multiples_allowed_true.id,
                )
            ]
        )
        # 15 / 5 => 3
        self.assertEqual(
            len(lot), 3, msg="The number of created lots should be equal to 3"
        )

    def test_multiples_allowed_true_2_multicompany(self):
        """
        Check that the picking has been created if
        the "multi-company" function is enabled
        """
        self._create_picking(multicompany=True)
        self._create_move(
            product=self.product_serial_auto_qty_5_multiples_allowed_true,
            qty=15.0,
            multicompany=True,
        )
        self.picking.with_company(self.company_2).button_validate()
        # Check the display field
        move = self.picking.move_ids.filtered(
            lambda m: m.product_id
            == self.product_serial_auto_qty_5_multiples_allowed_true
        )
        self.assertFalse(
            move.display_assign_serial, msg="Do not display the assigned serial number"
        )

        # Search for serials
        lot = self.env["stock.lot"].search(
            [
                (
                    "product_id",
                    "=",
                    self.product_serial_auto_qty_5_multiples_allowed_true.id,
                )
            ]
        )
        # 15 / 5 => 3
        self.assertEqual(
            len(lot), 3, msg="The number of created lots should be equal to 3"
        )

    def test_onchange_tracking(self):
        """Test the creation of a serial number if the tracking is equal to "none" """
        self.product_no_tracking.product_tmpl_id.tracking = "none"
        self.product_no_tracking.product_tmpl_id._onchange_tracking()
        self.assertFalse(
            self.product_no_tracking.product_tmpl_id.create_lot_every_n,
            msg="Tracking must be equal False",
        )

    def test_product_0_every_n(self):
        """Test the creation of a serial number if the create auto lot is equal to 0"""
        self._create_picking()
        self._create_move(
            product=self.product_0_every_n,
            qty=3,
        )
        self.picking.button_validate()
        self.assertTrue(
            self.picking.move_line_ids_without_package[0].lot_name,
            msg="The serial number must be created",
        )

    def test_prepare_stock_move_lines_for_lots_1(self):
        """
        Test case for preparing stock move lines for lots creation.
        """
        self._create_picking()
        # Validate that the quantity for creating lots must be greater than 0
        with self.assertRaises(
            ValidationError,
            msg="The qty create lot every n and product qty must be greater than 0",
        ):
            self.picking._prepare_stock_move_lines_for_lots(
                self.product_0_every_n, self.picking.move_line_ids, 1
            )

        # Validate that the product quantity must be greater than 0
        product = self.product_serial_auto_qty_5_multiples_allowed_false
        with self.assertRaises(
            ValidationError,
            msg="The qty create lot every n and product qty must be greater than 0",
        ):
            self.picking._prepare_stock_move_lines_for_lots(
                product, self.picking.move_line_ids, 0
            )

    def test_prepare_stock_move_lines_for_lots_2(self):
        """
        This test case covers various scenarios related to preparing stock move lines
        for creating lots, including validation checks and assertions on the generated lots.
        """
        self._create_picking()
        product_id = self.product_serial_auto_qty_5_multiples_allowed_false
        # Create a move with a specified product quantity
        self._create_move(product=product_id, qty=13.0)

        lines, new_lines = self.picking._split_stock_move_lines(self.picking)

        # Validate the number of lines and new lines
        self.assertEqual(len(lines), 1, msg="The number of lines should be equal to 1")
        self.assertEqual(
            len(new_lines), 0, msg="The number of new lines should be equal to 0"
        )

        # Prepare and validate the number of lots generated for the product
        current_product_qty = lines[0].reserved_uom_qty
        lots = self.picking._prepare_stock_move_lines_for_lots(
            product_id, lines[0], current_product_qty
        )

        self.assertEqual(
            len(lots),
            3,
            msg="The number of created lots should be equal to 3",
        )

    def test_prepare_stock_move_lines_for_lots_3(self):
        """
        This test case covers various scenarios related to preparing stock move lines
        for creating lots, including validation checks and assertions on the generated lots.
        """
        self._create_picking()
        product_1 = self.product_serial_auto_qty_5_multiples_allowed_false
        product_2 = self.product_serial_auto_qty_5_multiples_allowed_true
        location_dest_id = self.picking.picking_type_id.default_location_dest_id
        # Create a move with a specified product quantity
        self._create_move(product=product_1, qty=13.0)
        self.move.move_line_ids = [
            (
                0,
                0,
                {
                    "product_id": product_2.id,
                    "reserved_uom_qty": 5,
                    "product_uom_id": product_2.uom_id.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": location_dest_id.id,
                    "picking_id": self.picking.id,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": product_1.id,
                    "reserved_uom_qty": 3,
                    "product_uom_id": product_1.uom_id.id,
                    "location_id": self.supplier_location.id,
                    "location_dest_id": location_dest_id.id,
                    "picking_id": self.picking.id,
                },
            ),
        ]
        lines, new_lines = self.picking._split_stock_move_lines(self.picking)

        # Validate the number of lines and new lines
        self.assertEqual(len(lines), 3, msg="The number of lines should be equal to 3")
        self.assertEqual(
            len(new_lines), 0, msg="The number of new lines should be equal to 0"
        )

        # Prepare and validate the number of lots generated for the product
        lots = self.env["stock.move.line"].browse()
        for line in lines:
            lots |= self.picking._prepare_stock_move_lines_for_lots(
                line.product_id, line, line.reserved_uom_qty
            )
        # product 1 --> lot(3) 13/5 = 3
        # product 2 --> lot(1) 5/5 = 1
        # product 1 --> lot(1) 1/5 = 1
        self.assertEqual(
            len(lots),
            5,
            msg="The number of created lots should be equal to 5",
        )

    def test_multiples_allowed_false_immediate_transfer(self):
        """
        Test that the serial number is created if the quantity
        received is not a multiple of the selected value (Immediate Transfer)
        """
        self._create_picking(immediate_transfer=True)
        self._create_move(
            product=self.product_serial_auto_qty_5_multiples_allowed_false,
            qty=8.0,
            immediate_transfer=True,
        )
        self.picking.button_validate()
        # Check the display field
        move = self.picking.move_ids.filtered(
            lambda m: m.product_id
            == self.product_serial_auto_qty_5_multiples_allowed_false
        )
        self.assertFalse(
            move.display_assign_serial, msg="Do not display the assigned serial number"
        )

        # Search for serials
        lot = self.lot_obj.search(
            [
                (
                    "product_id",
                    "=",
                    self.product_serial_auto_qty_5_multiples_allowed_false.id,
                )
            ]
        )
        self.assertEqual(
            len(lot), 2, msg="The number of created lots should be equal to 2"
        )

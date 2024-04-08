# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError

from .common import CommonStockPickingAutoCreateLotQty


class TestStockPickingAutoCreateLotQty(CommonStockPickingAutoCreateLotQty):
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
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id
            == self.product_serial_auto_qty_5_multiples_allowed_false
        )
        self.assertFalse(
            move.display_assign_serial, msg="Do not display the assigned serial number"
        )

        # Search for serials
        lot = self.env["stock.production.lot"].search(
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
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id
            == self.product_serial_auto_qty_5_multiples_allowed_true
        )
        self.assertFalse(
            move.display_assign_serial, msg="Do not display the assigned serial number"
        )

        # Search for serials
        lot = self.env["stock.production.lot"].search(
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
        move = self.picking.move_lines.filtered(
            lambda m: m.product_id
            == self.product_serial_auto_qty_5_multiples_allowed_true
        )
        self.assertFalse(
            move.display_assign_serial, msg="Do not display the assigned serial number"
        )

        # Search for serials
        lot = self.env["stock.production.lot"].search(
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
        """Test tracking if the value is not 'lot'"""
        self.product_no_tracking.product_tmpl_id.tracking = "none"
        self.product_no_tracking.product_tmpl_id._onchange_tracking()
        self.assertFalse(
            self.product_no_tracking.product_tmpl_id.create_lot_every_n,
            msg="Tracking must be equal False",
        )

    def test_product_0_every_n(self):
        """Test when every n=0 create 0 lots"""
        self._create_picking()
        self._create_move(
            product=self.product_0_every_n,
            qty=5,
        )
        self.picking.button_validate()

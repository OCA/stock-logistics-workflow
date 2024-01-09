# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestExpirationDateRequired(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_in.use_create_lots = True
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Expiration Product",
                "type": "product",
                "use_expiration_date": True,
                "expiration_time": 0,
                "tracking": "lot",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Expiration Partner"})
        picking_form = Form(cls.env["stock.picking"])
        picking_form.partner_id = cls.partner
        picking_form.picking_type_id = cls.picking_type_in
        with picking_form.move_ids_without_package.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 10
        cls.picking = picking_form.save()

    def test_expiration_date_required_and_not_auto_calculated(self):
        """Test that the expiration date is required for the stock move line
        and it's not auto-calculated"""
        self.picking.action_confirm()
        move_form = Form(
            self.picking.move_ids_without_package,
            view="stock.view_stock_move_operations",
        )
        with self.assertRaisesRegex(
            AssertionError, "expiration_date is a required field"
        ):
            with move_form.move_line_ids.new() as move_line_tree:
                move_line_tree.lot_name = "TLE1"
                move_line_tree.qty_done = 1
                self.assertEqual(move_line_tree.expiration_date, False)

    def test_expiration_date_auto_caulculated(self):
        """Test that the expiration date is auto-calculated
        if expiration_date is set in the product"""
        self.product.expiration_time = 10
        self.picking.action_confirm()
        move_form = Form(
            self.picking.move_ids_without_package,
            view="stock.view_stock_move_operations",
        )
        with move_form.move_line_ids.new() as move_line_tree:
            move_line_tree.lot_name = "TLE2"
            move_line_tree.qty_done = 1
            self.assertNotEqual(move_line_tree.expiration_date, False)
        move_form.save()

    def test_expiration_date_generate_serials(self):
        """Test that the expiration date is not auto-calculated
        when generating serial numbers"""
        self.product.tracking = "serial"
        # Create new picking with product tracking: serial
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.picking_type_in
        with picking_form.move_ids_without_package.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 10
        picking = picking_form.save()
        picking.action_confirm()
        # Prepare serial generation
        move = picking.move_ids_without_package
        move.next_serial = "001"
        move.next_serial_count = move.product_uom_qty
        picking.move_ids_without_package._generate_serial_numbers()
        # Check expiration date is empty
        for move_line in picking.move_line_ids:
            self.assertEqual(move_line.expiration_date, False)
        # Ensure picking validation is not allowed
        with self.assertRaisesRegex(UserError, "expiration date"):
            # Ensure run sanity_check
            picking.with_context(skip_sanity_check=False).button_validate()

    def test_lot_no_expiration_date(self):
        """Test that lots without expiration dates works properly"""
        self.product.use_expiration_date = False
        self.picking.action_confirm()
        move_form = Form(
            self.picking.move_ids_without_package,
            view="stock.view_stock_move_operations",
        )
        with move_form.move_line_ids.new() as move_line_tree:
            move_line_tree.lot_name = "TLE3"
            move_line_tree.qty_done = 10
        move_form.save()
        self.picking.with_context(skip_sanity_check=False).button_validate()

    def test_serials_no_expiration_date(self):
        """Test that serials without expiration dates works proplerly"""
        self.product.tracking = "serial"
        self.product.use_expiration_date = False
        # Create new picking with product tracking: serial
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.picking_type_in
        with picking_form.move_ids_without_package.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 10
        picking = picking_form.save()
        picking.action_confirm()
        # Prepare serial generation
        move = picking.move_ids_without_package
        move.next_serial = "001"
        move.next_serial_count = move.product_uom_qty
        picking.move_ids_without_package._generate_serial_numbers()
        picking.with_context(skip_sanity_check=False).button_validate()

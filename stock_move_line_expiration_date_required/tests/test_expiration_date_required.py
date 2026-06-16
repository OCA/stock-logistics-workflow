# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo import fields
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
                "type": "consu",
                "use_expiration_date": True,
                "expiration_time": 0,
                "tracking": "lot",
            }
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test Source Location",
                "usage": "internal",
                "company_id": cls.env.company.id,
            }
        )
        cls.location_dest = cls.env["stock.location"].create(
            {
                "name": "Test Dest Location",
                "usage": "internal",
                "company_id": cls.env.company.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Expiration Partner"})
        picking_form = Form(cls.env["stock.picking"])
        picking_form.partner_id = cls.partner
        picking_form.picking_type_id = cls.picking_type_in
        with picking_form.move_ids.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 10
        cls.picking = picking_form.save()

    def test_expiration_date_required_and_not_auto_calculated(self):
        """Test that the expiration date is required for the stock move line
        and it's not auto-calculated"""
        self.picking.action_confirm()
        move_form = Form(
            self.picking.move_ids,
            view="stock.view_stock_move_operations",
        )
        with self.assertRaisesRegex(
            AssertionError, "'expiration_date' is a required field"
        ):
            with move_form.move_line_ids.edit(0) as move_line_tree:
                move_line_tree.lot_name = "TLE1"
                move_line_tree.quantity = 1
                self.assertEqual(move_line_tree.expiration_date, False)

    def test_expiration_date_auto_caulculated(self):
        """Test that the expiration date is auto-calculated
        if expiration_date is set in the product"""
        self.product.expiration_time = 10
        self.picking.action_confirm()
        move_form = Form(
            self.picking.move_ids,
            view="stock.view_stock_move_operations",
        )
        with move_form.move_line_ids.edit(0) as move_line_tree:
            move_line_tree.lot_name = "TLE2"
            move_line_tree.quantity = 1
            self.assertNotEqual(move_line_tree.expiration_date, False)
        move_form.save()

    def test_expiration_date_generate_serials(self):
        """Test that the expiration date is auto-calculated
        when generating serial numbers"""

        self.product.tracking = "serial"
        self.product.expiration_time = 10

        # Create new picking with product tracking: serial
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.picking_type_in

        with picking_form.move_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 10

        picking = picking_form.save()
        picking.action_confirm()

        # Prepare serial generation
        move = picking.move_ids
        move.next_serial_count = move.product_uom_qty
        picking.move_ids._generate_serial_numbers("001")

        # Check expiration date is computed (NOT empty anymore)
        for move_line in picking.move_line_ids:
            self.assertTrue(move_line.expiration_date)

        # Ensure picking validation is not allowed
        picking.with_context(skip_sanity_check=False).button_validate()
        self.assertTrue(all(picking.move_line_ids.mapped("expiration_date")))

    def test_lot_no_expiration_date(self):
        """Test that lots without expiration dates works properly"""
        self.product.use_expiration_date = False
        self.picking.action_confirm()
        move_form = Form(
            self.picking.move_ids,
            view="stock.view_stock_move_operations",
        )
        with move_form.move_line_ids.edit(0) as move_line_tree:
            move_line_tree.lot_name = "TLE3"
            move_line_tree.quantity = 10
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
        with picking_form.move_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 10
        picking = picking_form.save()
        picking.action_confirm()
        # Prepare serial generation
        move = picking.move_ids
        move.next_serial_count = move.product_uom_qty
        picking.move_ids._generate_serial_numbers("001")
        picking.with_context(skip_sanity_check=False).button_validate()

    def test_compute_expiration_date_existing_lot_expiration(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-EXP",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )

        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.picking_type_in

        with picking_form.move_ids.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 1

        picking = picking_form.save()
        picking.action_confirm()

        move_line = picking.move_line_ids[0]
        move_line.lot_id = lot

        move_line._compute_expiration_date()

        self.assertEqual(
            move_line.expiration_date,
            move_line.lot_id.expiration_date,
        )

    def test_compute_expiration_date_already_set(self):
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.picking_type_in

        with picking_form.move_ids.new() as move:
            move.product_id = self.product
            move.product_uom_qty = 1

        picking = picking_form.save()
        picking.action_confirm()

        move_line = picking.move_line_ids[0]
        move_line.expiration_date = fields.Datetime.now()

        move_line._compute_expiration_date()

        self.assertTrue(move_line.expiration_date)

    def test_onchange_product_id_sets_expiration_date(self):
        self.product.expiration_time = 10

        move_line = self.env["stock.move.line"].new(
            {
                "product_id": self.product.id,
                "picking_type_use_create_lots": True,
            }
        )

        move_line._onchange_product_id()

        self.assertTrue(move_line.expiration_date)

    def test_onchange_product_id_without_expiration(self):
        self.product.use_expiration_date = False

        move_line = self.env["stock.move.line"].new(
            {
                "product_id": self.product.id,
                "picking_type_use_create_lots": True,
            }
        )

        move_line._onchange_product_id()

        self.assertFalse(move_line.expiration_date)

    def test_sanity_check_raises_when_missing_expiration_date(self):
        """Test that validation raises UserError when move line
        has use_expiration_date=True but expiration_date is not set."""
        self.product.expiration_time = 0  # Prevent auto-calculation
        self.picking.action_confirm()

        move_line = self.picking.move_line_ids[0]
        move_line.lot_name = "TLE_NO_EXP"
        move_line.quantity = 10
        move_line.expiration_date = False

        with self.assertRaisesRegex(
            UserError,
            self.product.display_name,
        ):
            self.picking.with_context(skip_sanity_check=False)._sanity_check()

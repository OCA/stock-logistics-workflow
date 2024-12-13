# Copyright 2024 Cetmix OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockReturnPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_return = cls.env["stock.return.picking"]
        cls.picking_return_line = cls.env["stock.return.picking.line"]
        cls.stock_move = cls.env["stock.move"]
        cls.product_template = cls.env["product.template"]
        cls.config_obj = cls.env["res.config.settings"].sudo()
        product_template_a = cls.product_template.create(
            {"name": "Product A", "type": "product"}
        )
        product_template_b = cls.product_template.create(
            {"name": "Product B", "type": "product"}
        )
        cls.product_a = product_template_a.product_variant_id
        cls.product_b = product_template_b.product_variant_id

    @classmethod
    def _create_picking(cls, location, destination_location, picking_type):
        return cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": location.id,
                "location_dest_id": destination_location.id,
            }
        )

    @classmethod
    def _create_move(cls, picking, product, qty):
        return cls.stock_move.create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": qty,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )

    def test_00(self):
        """
        Check the return process when the option in Settings
        'Stock Picking Return Quantity Limit' is enabled
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )

        move_1 = self._create_move(picking=picking, product=self.product_a, qty=2)
        move_2 = self._create_move(picking=picking, product=self.product_b, qty=1)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 2
        move_2.quantity_done = 1
        picking.button_validate()
        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()
        return_qty_limit = return_wizard.product_return_moves[
            0
        ]._check_return_limit_enforcement()
        self.assertTrue(
            return_qty_limit,
            msg="'Stock Picking Return Quantity Limit' must be enabled",
        )

        for line in return_wizard.product_return_moves:
            self.assertEqual(
                line.quantity,
                line.quantity_max,
                msg="Return Quantity must be equal to the maximum quantity",
            )
            with self.assertRaises(ValidationError):
                line.quantity = line.quantity + 1

    def test_01(self):
        """
        Check the return process when the option in Settings
        'Stock Picking Return Quantity Limit' is disabled
        """

        config = self.config_obj.create({"stock_picking_limit_return_qty": False})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move_1 = self._create_move(picking=picking, product=self.product_a, qty=2)
        move_2 = self._create_move(picking=picking, product=self.product_b, qty=1)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 2
        move_2.quantity_done = 1
        picking.button_validate()
        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()
        return_qty_limit = return_wizard.product_return_moves[
            0
        ]._check_return_limit_enforcement()
        self.assertFalse(
            return_qty_limit,
            msg="'Stock Picking Return Quantity Limit' must be disabled",
        )

        for line in return_wizard.product_return_moves:
            line.quantity = line.quantity + 1
            self.assertNotEqual(
                line.quantity,
                line.quantity_max,
                msg="Return Quantity must be not equal to the maximum quantity",
            )

    def test_check_return_limit_enforcement_enabled(self):
        """
        Test that the return limit enforcement is enabled when the configuration
        specifies that the stock picking return quantity limit should be enabled.

        This test creates a configuration with the stock picking return quantity
        limit enabled, executes the configuration, and then checks that the return
        limit enforcement is indeed enabled.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        self.assertTrue(
            self.picking_return_line._check_return_limit_enforcement(),
            msg="Stock Picking Return Quantity Limit must be enabled",
        )

    def test_check_return_limit_enforcement_disabled(self):
        """
        Test that the return limit enforcement is disabled when the configuration
        specifies that the stock picking return quantity limit should be disabled.

        This test creates a configuration with the stock picking return quantity
        limit disabled, executes the configuration, and then checks that the return
        limit enforcement is indeed disabled.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": False})
        config.execute()
        self.assertFalse(
            self.picking_return_line._check_return_limit_enforcement(),
            msg="Stock Picking Return Quantity Limit must be disabled",
        )

    def test_zero_quantity(self):
        """
        Test the return process with zero quantity.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move_1 = self._create_move(picking=picking, product=self.product_a, qty=0)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 0
        with self.assertRaises(UserError):
            picking.button_validate()

    def test_partial_quantity(self):
        """
        Test the return process with partial quantity.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move_1 = self._create_move(picking=picking, product=self.product_a, qty=5)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 5
        picking.button_validate()
        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()
        for line in return_wizard.product_return_moves:
            line.quantity = 3
            self.assertEqual(line.quantity, 3, msg="Return Quantity must be 3")

    def test_multiple_products(self):
        """
        Test the return process with multiple products.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move_1 = self._create_move(picking=picking, product=self.product_a, qty=2)
        move_2 = self._create_move(picking=picking, product=self.product_b, qty=3)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 2
        move_2.quantity_done = 3
        picking.button_validate()
        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()
        for line in return_wizard.product_return_moves:
            self.assertEqual(
                line.quantity,
                line.quantity_max,
                msg="Return Quantity must be equal to the maximum quantity",
            )

    def test_no_products(self):
        """
        Test the return process with no products.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        picking.action_confirm()
        with self.assertRaises(UserError):
            picking.action_assign()

    def test_invalid_configuration(self):
        """
        Test the return process with invalid configuration.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": None})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move_1 = self._create_move(picking=picking, product=self.product_a, qty=2)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 2
        picking.button_validate()
        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()
        return_qty_limit = return_wizard.product_return_moves[
            0
        ]._check_return_limit_enforcement()
        self.assertFalse(
            return_qty_limit,
            msg=(
                "'Stock Picking Return Quantity Limit'"
                "must be disabled with invalid configuration"
            ),
        )

    def test_prepare_stock_return_picking_line_vals_from_move(self):
        """
        Test the _prepare_stock_return_picking_line_vals_from_move method.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move_1 = self._create_move(picking=picking, product=self.product_a, qty=2)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 2
        picking.button_validate()

        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()

        for line in return_wizard.product_return_moves:
            res = return_wizard._prepare_stock_return_picking_line_vals_from_move(
                line.move_id
            )
            self.assertEqual(
                res["quantity_max"],
                line.quantity_max,
                msg="Quantity max must be equal to the return quantity max",
            )

    def test_constraints_quantity(self):
        """
        Test the _constraints_quantity method.
        """
        config = self.config_obj.create({"stock_picking_limit_return_qty": True})
        config.execute()
        picking = self._create_picking(
            self.supplier_location, self.stock_location, self.picking_type_in
        )
        move_1 = self._create_move(picking=picking, product=self.product_a, qty=2)
        picking.action_confirm()
        picking.action_assign()
        move_1.quantity_done = 2
        picking.button_validate()

        return_wizard = self.picking_return.with_context(
            active_id=picking.id, active_model="stock.picking"
        ).create({})
        return_wizard._onchange_picking_id()

        for line in return_wizard.product_return_moves:
            with self.assertRaises(
                ValidationError,
                msg=(
                    "ValidationError must be raised when "
                    "quantity exceeds the maximum allowed quantity"
                ),
            ):
                line.quantity = line.quantity_max + 1

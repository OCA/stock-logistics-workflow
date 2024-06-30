# Copyright 2024 Cetmix OU
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
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
        cls.product_product = cls.env["product.product"]
        cls.config_obj = cls.env["res.config.settings"].sudo()
        cls.product_a = cls.product_product.create(
            {"name": "Product A", "type": "product"}
        )
        cls.product_b = cls.product_product.create(
            {"name": "Product B", "type": "product"}
        )

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
        return_line = return_wizard.product_return_moves[
            0
        ]._check_return_limit_enforcement()
        self.assertTrue(
            return_line, msg="'Stock Picking Return Quantity Limit' must be enabled"
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
        return_line = return_wizard.product_return_moves[
            0
        ]._check_return_limit_enforcement()
        self.assertFalse(
            return_line, msg="'Stock Picking Return Quantity Limit' must be disabled"
        )

        for line in return_wizard.product_return_moves:
            self.assertEqual(
                line.quantity,
                line.quantity_max,
                msg="Return Quantity must be equal to the maximum quantity",
            )
            line.quantity = line.quantity + 1

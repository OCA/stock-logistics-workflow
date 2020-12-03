# Copyright 2015-2016 Akretion (http://www.akretion.com) - Alexis de Lattre
# Copyright 2016 ForgeFlow (http://www.forgeflow.com)
# Copyright 2016 Serpent Consulting Services (<http://www.serpentcs.com>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockNoNegative(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestStockNoNegative, self).setUp()
        self.product_model = self.env["product.product"]
        self.product_ctg_model = self.env["product.category"]
        self.picking_type_id = self.env.ref("stock.picking_type_out")
        self.location_id = self.env.ref("stock.stock_location_stock")
        self.location_dest_id = self.env.ref("stock.stock_location_customers")
        # Create product category
        self.product_ctg = self._create_product_category()
        # Create a Product
        self.product = self._create_product("test_product1")
        self._create_picking()

    def _create_product_category(self):
        product_ctg = self.product_ctg_model.create(
            {"name": "test_product_ctg", "allow_negative_stock": False}
        )
        return product_ctg

    def _create_product(self, name):
        product = self.product_model.create(
            {
                "name": name,
                "categ_id": self.product_ctg.id,
                "type": "product",
                "allow_negative_stock": False,
            }
        )
        return product

    def _create_picking(self):
        self.stock_picking = (
            self.env["stock.picking"]
            .with_context(test_stock_no_negative=True)
            .create(
                {
                    "picking_type_id": self.picking_type_id.id,
                    "move_type": "direct",
                    "location_id": self.location_id.id,
                    "location_dest_id": self.location_dest_id.id,
                }
            )
        )

        self.stock_move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": 100.0,
                "product_uom": self.product.uom_id.id,
                "picking_id": self.stock_picking.id,
                "state": "draft",
                "location_id": self.location_id.id,
                "location_dest_id": self.location_dest_id.id,
                "quantity_done": 100.0,
            }
        )

    def test_check_constrains(self):
        """Assert that constraint is raised when user
        tries to validate the stock operation which would
        make the stock level of the product negative"""
        self.stock_picking.action_confirm()
        with self.assertRaises(ValidationError):
            self.stock_picking.button_validate()

    def test_true_allow_negative_stock_product(self):
        """Assert that negative stock levels are allowed when
        the allow_negative_stock is set active in the product"""
        self.product.allow_negative_stock = True
        self.stock_picking.action_confirm()
        self.stock_picking.button_validate()
        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.location_id.id),
            ]
        )
        self.assertEqual(quant.quantity, -100)

    def test_true_allow_negative_stock_location(self):
        """Assert that negative stock levels are allowed when
        the allow_negative_stock is set active in the product"""
        self.product.allow_negative_stock = False
        self.location_id.allow_negative_stock = True
        self.stock_picking.action_confirm()
        self.stock_picking.button_validate()
        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.location_id.id),
            ]
        )
        self.assertEqual(quant.quantity, -100)

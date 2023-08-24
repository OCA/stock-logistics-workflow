# Copyright 2023 Your Company Name
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockNoNegativeMoveLine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_model = cls.env["product.product"]
        cls.product_ctg_model = cls.env["product.category"]
        cls.picking_type_id = cls.env.ref("stock.picking_type_out")
        cls.location_id = cls.env.ref("stock.stock_location_stock")
        cls.location_dest_id = cls.env.ref("stock.stock_location_customers")
        # Create product category
        cls.product_ctg = cls._create_product_category(cls)
        # Create a Product
        cls.product = cls._create_product(cls, "test_product1")
        cls._create_picking(cls)

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
            }
        )

        self.stock_move_line = self.env["stock.move.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "picking_id": self.stock_picking.id,
                "move_id": self.stock_move.id,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_dest_id.id,
                "qty_done": 0.0,
            }
        )

    def test_check_negative_qty_on_move_line(self):
        """Assert that constraint is raised when user tries to update the qty_done
        on the move line which would make the stock level of the product negative"""
        self.env.company.prevent_negative_quantity_on = "move_line"
        self.product.allow_negative_stock = False
        self.product.categ_id.allow_negative_stock = False
        self.location_id.allow_negative_stock = False
        self.stock_picking.action_confirm()
        with self.assertRaises(ValidationError):
            self.stock_move_line.write({"qty_done": 150.0})
            self.stock_move_line.check_negative_qty()

    def test_allow_negative_stock_product_on_move_line(self):
        """Assert that negative stock levels are allowed on move line update when
        the allow_negative_stock is set active in the product"""
        self.env.company.prevent_negative_quantity_on = "move_line"
        self.product.allow_negative_stock = True
        self.product.categ_id.allow_negative_stock = False
        self.location_id.allow_negative_stock = False
        self.stock_picking.action_confirm()

        self.stock_move_line.write({"qty_done": 150.0})
        self.stock_move_line.check_negative_qty()
        self.stock_picking._action_done()

        quant = self.env["stock.quant"]._gather(
            self.product, self.location_id, lot_id=self.stock_move_line.lot_id,
            package_id=self.stock_move_line.package_id, owner_id=self.stock_move_line.owner_id, strict=True
        )
        self.assertEqual(quant.quantity, -150)

    def test_allow_negative_stock_location_on_move_line(self):
        """Assert that negative stock levels are allowed on move line update when
        the allow_negative_stock is set active in the location"""
        self.env.company.prevent_negative_quantity_on = "move_line"
        self.product.allow_negative_stock = False
        self.product.categ_id.allow_negative_stock = False
        self.stock_move_line.location_id.allow_negative_stock = True
        self.stock_picking.action_confirm()
        self.stock_move_line.write({"qty_done": 150.0})
        self.stock_move_line.check_negative_qty()
        self.stock_picking._action_done()
        quant = self.env["stock.quant"]._gather(
            self.product, self.location_id, lot_id=self.stock_move_line.lot_id,
            package_id=self.stock_move_line.package_id, owner_id=self.stock_move_line.owner_id, strict=True
        )
        self.assertEqual(quant.quantity, -150)

    def test_negative_qty_prevention_on_validation(self):
        """Assert that negative stock levels are prevented on validation and not on move line update"""
        self.env.company.prevent_negative_quantity_on = "validation"
        self.stock_picking.action_confirm()
        self.stock_move_line.write({"qty_done": 150.0})
        with self.assertRaises(ValidationError):
            self.stock_picking.with_context(test_stock_no_negative=True).button_validate()

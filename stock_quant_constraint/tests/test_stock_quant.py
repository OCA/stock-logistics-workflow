# Copyright 2021 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockQuant(TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        super().setUp()
        # Setup models used.
        self.quant_model = self.env["stock.quant"]
        self.product_model = self.env["product.product"]
        self.product_category_model = self.env["product.category"]
        # Link to standard records.
        self.picking_type = self.env.ref("stock.picking_type_out")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.destination_location = self.env.ref("stock.stock_location_customers")
        # Create test data.
        self.product_category = self._create_product_category()
        self.product = self._create_product("test_product1")
        self._create_picking()

    def _create_product_category(self):
        product_category = self.product_category_model.create(
            {"name": "test_product_category", "allow_negative_stock": False}
        )
        return product_category

    def _create_product(self, name):
        product = self.product_model.create(
            {"name": name, "categ_id": self.product_category.id, "type": "product"}
        )
        # make some stock
        self.quant_model._update_available_quantity(product, self.stock_location, 100)
        self.assertEqual(
            self.quant_model._get_available_quantity(product, self.stock_location),
            100.0,
        )
        return product

    def _create_picking(self):
        """Create picking for  product. This will create a reservation automagically."""
        self.stock_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "move_type": "direct",
                "location_id": self.stock_location.id,
                "location_dest_id": self.destination_location.id,
            }
        )
        self.stock_move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": 10.0,
                "product_uom": self.product.uom_id.id,
                "picking_id": self.stock_picking.id,
                "state": "draft",
                "location_id": self.stock_location.id,
                "location_dest_id": self.destination_location.id,
                "quantity_done": 10.0,
            }
        )

    def test_check_constrains(self):
        """Quant reservations should always be consistent with line reservations."""
        # Find quant for product.
        stock_quant = self.quant_model.search(
            [
                ("location_id", "=", self.stock_location.id),
                ("product_id", "=", self.product.id),
            ],
            limit=1,
        )
        self.assertEqual(stock_quant.reserved_quantity, 0.0)
        self.stock_picking.action_assign()
        self.assertEqual(stock_quant.reserved_quantity, 10.0)
        with self.assertRaises(ValidationError):
            self.quant_model.write({"reserved_quantity": 5.0})

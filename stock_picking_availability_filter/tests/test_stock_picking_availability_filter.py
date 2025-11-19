# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingAvailabilityFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockPicking = cls.env["stock.picking"]
        cls.ProductProduct = cls.env["product.product"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockQuant = cls.env["stock.quant"]

        # Get locations
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        # Create products
        cls.product_available = cls._create_product("Available Product")
        cls.product_unavailable = cls._create_product("Unavailable Product")

        # Create quants to make products available
        cls._create_quant(cls.product_available, 100.0, cls.stock_location)

    @classmethod
    def _create_product(cls, name, **kwargs):
        """Helper to create a product"""
        vals = {
            "name": name,
            "type": "product",
            "tracking": "none",
        }
        vals.update(kwargs)
        return cls.ProductProduct.create(vals)

    @classmethod
    def _create_quant(cls, product, quantity, location):
        """Create a quant for the product in the given location"""
        return cls.StockQuant.create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "quantity": quantity,
            }
        )

    def _create_picking(
        self, product, qty, location_src=None, location_dest=None, **kwargs
    ):
        """Helper to create a picking with a single move"""
        location_src = location_src or self.stock_location
        location_dest = location_dest or self.customer_location

        picking_vals = {
            "picking_type_id": self.env.ref("stock.picking_type_out").id,
            "location_id": location_src.id,
            "location_dest_id": location_dest.id,
            "move_ids": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "product_uom": product.uom_id.id,
                        "location_id": location_src.id,
                        "location_dest_id": location_dest.id,
                    },
                )
            ],
        }
        picking_vals.update(kwargs)
        return self.StockPicking.create(picking_vals)

    def _create_multi_move_picking(
        self, moves_data, location_src=None, location_dest=None
    ):
        """Helper to create a picking with multiple moves"""
        location_src = location_src or self.stock_location
        location_dest = location_dest or self.customer_location

        move_vals = []
        for move_data in moves_data:
            product = move_data["product"]
            move_vals.append(
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": move_data["qty"],
                        "product_uom": product.uom_id.id,
                        "location_id": move_data.get("location_src", location_src).id,
                        "location_dest_id": move_data.get(
                            "location_dest", location_dest
                        ).id,
                    },
                )
            )

        return self.StockPicking.create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": location_src.id,
                "location_dest_id": location_dest.id,
                "move_ids": move_vals,
            }
        )

    def _confirm_and_assign(self, picking):
        """Helper to confirm and assign a picking"""
        picking.action_confirm()
        picking.action_assign()
        return picking

    def test_01_search_available(self):
        """Test search for available pickings"""
        # Create and process a picking with available product
        picking = self._create_picking(product=self.product_available, qty=5.0)
        self._confirm_and_assign(picking)

        # Search for available pickings
        available_pickings = self.StockPicking.search(
            [("products_availability", "=", "available")]
        )

        # The picking should be in the available pickings
        self.assertIn(picking, available_pickings)

    def test_02_search_expected(self):
        """Test search for expected pickings"""
        picking = self._create_picking(
            product=self.product_unavailable,
            qty=5.0,
            location_src=self.supplier_location,
            location_dest=self.stock_location,
        )
        self._confirm_and_assign(picking)

        # Create a picking with one available and one unavailable product
        picking = self._create_multi_move_picking(
            [
                {"product": self.product_available, "qty": 5.0},
                {"product": self.product_unavailable, "qty": 5.0},
            ]
        )

        self._confirm_and_assign(picking)

        # Search for expected pickings using ilike 'Exp'
        expected_pickings = self.StockPicking.search(
            [("products_availability", "=", "expected")]
        )

        # The picking should be in the expected pickings
        self.assertIn(picking, expected_pickings)

    def test_03_search_not_available(self):
        """Test search for not available pickings"""
        # Create a picking with a product that's not in stock
        picking = self._create_picking(product=self.product_unavailable, qty=5.0)
        picking.action_confirm()  # Don't assign as it's not available

        # Search for not available pickings
        not_available_pickings = self.StockPicking.search(
            [("products_availability", "=", "late")]
        )

        # The picking should be in the not available pickings
        self.assertIn(picking, not_available_pickings)

    def test_04_search_invalid_operator(self):
        """Test search with invalid operator"""
        # Search with an invalid operator
        result = self.StockPicking._search_products_availability("!=", "Test")
        self.assertEqual(result, [])

        # Search with empty value
        result = self.StockPicking._search_products_availability("=", False)
        self.assertEqual(result, [])

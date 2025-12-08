from odoo.tests import TransactionCase


class TestProductProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a reference for the limited amount
        cls.limited_amount_lq = cls.env.ref(
            "l10n_eu_product_adr_dangerous_goods.limited_amount_1"
        )
        # Create a product that is dangerous and has the limited amount
        cls.dangerous_product = cls.env["product.product"].create(
            {
                "name": "Dangerous Product",
                "is_dangerous": True,
                "limited_amount_id": cls.limited_amount_lq.id,
                "is_storable": True,
            }
        )
        # Create a product that is not dangerous
        cls.non_dangerous_product = cls.env["product.product"].create(
            {
                "name": "Non-Dangerous Product",
                "is_dangerous": False,
                "is_storable": True,
            }
        )
        # Create a product that is dangerous but does not have the limited amount
        cls.dangerous_product_no_limit = cls.env["product.product"].create(
            {
                "name": "Dangerous Product No Limit",
                "is_dangerous": True,
                "limited_amount_id": False,
            }
        )

        partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        # Create a stock picking
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            }
        )

    def test_is_lq_product(self):
        # Test the dangerous product with limited amount
        self.assertTrue(
            self.dangerous_product.is_lq_product,
            "The dangerous product should be a limited quantity product.",
        )

        # Test the non-dangerous product
        self.assertFalse(
            self.non_dangerous_product.is_lq_product,
            "The non-dangerous product should not be a limited quantity product.",
        )

        # Test the dangerous product without limited amount
        self.assertFalse(
            self.dangerous_product_no_limit.is_lq_product,
            "The dangerous product without limited amount should not be a limited"
            " quantity product.",
        )

    def test_has_lq_products_with_package(self):
        # Create stock move line for a dangerous product
        move_line_1 = self.env["stock.move.line"].create(
            {
                "picking_id": self.picking.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_id": self.dangerous_product.id,
                "quantity": 10,
            }
        )

        # Create stock move line for a non-dangerous product
        move_line_2 = self.env["stock.move.line"].create(
            {
                "picking_id": self.picking.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_id": self.non_dangerous_product.id,
                "quantity": 5,
            }
        )

        # Confirm picking and make it available to process
        self.picking.action_confirm()
        self.picking.action_assign()

        # Create a stock.quant.package
        package = self.env["stock.quant.package"].create(
            {
                "name": "Test Package",
            }
        )

        # Assign the move lines to the package
        move_line_1.package_id = package.id
        move_line_2.package_id = package.id

        # Simulate stock quant creation for the products
        self.env["stock.quant"]._update_available_quantity(
            self.dangerous_product,
            self.env.ref("stock.stock_location_stock"),
            10,
            package_id=package,
        )
        self.env["stock.quant"]._update_available_quantity(
            self.non_dangerous_product,
            self.env.ref("stock.stock_location_stock"),
            5,
            package_id=package,
        )

        # Validate that the package has LQ products
        self.assertTrue(
            package.has_lq_products,
            "The package should have LQ products as it contains a dangerous product.",
        )

        # Remove the dangerous product's quant
        dangerous_quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.dangerous_product.id),
                ("package_id", "=", package.id),
            ]
        )
        dangerous_quant.unlink()

        # Validate that the package no longer has LQ products
        self.assertFalse(
            package.has_lq_products,
            "The package should not have LQ products after removing the dangerous"
            " product.",
        )

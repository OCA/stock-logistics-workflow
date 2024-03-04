# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase


class TestStockForceAssignByType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.receipt_type = cls.env.ref("stock.picking_type_in")
        cls.partner_supplier = cls.env["res.partner"].create(
            {
                "name": "Parner Supplier",
            }
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
            }
        )

    def _create_purchase_order(self):
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = self.partner_supplier
        with purchase_form.order_line.new() as purchase_line_form:
            purchase_line_form.product_id = self.product1
            purchase_line_form.product_qty = 10
        purchase = purchase_form.save()
        return purchase

    def test_01_stock_force_assign_by_type(self):
        self.partner_supplier.property_stock_supplier = self.stock_location
        # Make some stock
        self.env["stock.quant"]._update_available_quantity(
            self.product1, self.stock_location, 100
        )
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product1, self.stock_location
            ),
            100.0,
        )
        # Set forced reserve in the picking type
        self.receipt_type.force_reservation = True
        # Create a purchase order for a product
        purchase = self._create_purchase_order()
        purchase.button_confirm()
        # Check that the units have been reserved
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product1, self.stock_location
            ),
            90.0,
        )
        # Check picking
        picking = purchase.picking_ids
        # From picking you can unreserve and the stock will be available again.
        picking.do_unreserve()
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product1, self.stock_location
            ),
            100.0,
        )
        # You can reassign the reservation and it will be reflected in the stock again.
        picking.action_assign()
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product1, self.stock_location
            ),
            90.0,
        )

    def test_02_no_stock_force_assign_by_type(self):
        # Verify the usual behaviour.
        self.env["stock.quant"]._update_available_quantity(
            self.product1, self.stock_location, 100
        )
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product1, self.stock_location
            ),
            100.0,
        )
        # Create a purchase order for a product
        purchase = self._create_purchase_order()
        purchase.button_confirm()
        # Check that the units haven't been reserved
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product1, self.stock_location
            ),
            100.0,
        )

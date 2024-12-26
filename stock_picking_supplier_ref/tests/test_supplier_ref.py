from datetime import date

from odoo.tests.common import TransactionCase


class TestStockPickingSupplierReference(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a customer (since `sale` is installed)
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )

        # Create a product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
            }
        )

        # Create a sales order
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "date_order": date.today(),
            }
        )
        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
                "product_uom_qty": 10,
                "price_unit": 100,
            }
        )

        # Confirm the sales order to create a stock picking
        cls.sale_order.action_confirm()
        cls.stock_picking = cls.sale_order.picking_ids[0]

    def test_supplier_reference_in_picking(self):
        # Assign a supplier reference to the sale order
        self.sale_order.client_order_ref = "TEST-SUPPLIER-REF"

        # Manually set the supplier reference in the stock picking
        self.stock_picking.supplier_reference = self.sale_order.client_order_ref

        # Ensure the supplier reference is correctly set
        self.assertEqual(
            self.stock_picking.supplier_reference,
            "TEST-SUPPLIER-REF",
            "Supplier reference should be correctly set in the stock picking",
        )

    def test_supplier_reference_field_exists(self):
        # Check if the `supplier_reference` field exists in the `stock.picking` model
        self.assertTrue(
            hasattr(self.stock_picking, "supplier_reference"),
            "Field `supplier_reference` is not present in the stock.picking model",
        )

    def test_supplier_reference_empty_by_default(self):
        # Ensure that the `supplier_reference` is empty if not explicitly set
        self.assertFalse(
            self.stock_picking.supplier_reference,
            "Field `supplier_reference` should be empty by default",
        )

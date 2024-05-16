# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import users

from .common import TestStockCustomerDepositCommon


class TestDeliverCustomerDeposits(TestStockCustomerDepositCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        stock_dict = {
            cls.productA: {False: 300, cls.partner1: 100},
            cls.productB: {False: 400, cls.partner1: 120},
            cls.productC: {False: 500},
        }
        cls.update_availiable_quantity(cls, stock_dict)
        cls.result_test = {
            "sale1": {
                False: {
                    cls.productA: 300,
                    cls.productB: 400,
                    cls.productC: 410,
                },
                cls.partner1: {
                    cls.productA: 50,
                    cls.productB: 50,
                    cls.productC: 0,
                },
            },
            "sale2": {
                False: {
                    cls.productA: 300,
                    cls.productB: 400,
                    cls.productC: 410,
                },
                cls.partner1: {
                    cls.productA: 50,
                    cls.productB: 50,
                    cls.productC: 0,
                },
            },
            "sale3": {
                False: {
                    cls.productA: 250,
                    cls.productB: 330,
                    cls.productC: 410,
                },
                cls.partner1: {
                    cls.productA: 100,
                    cls.productB: 120,
                    cls.productC: 0,
                },
            },
            "sale6": {
                False: {
                    cls.productA: 100,
                    cls.productB: 200,
                    cls.productC: 300,
                },
                cls.partner1: {
                    cls.productA: 100,
                    cls.productB: 120,
                    cls.productC: 0,
                },
            },
            "sale7": {
                False: {
                    cls.productA: 0,
                    cls.productB: 0,
                    cls.productC: 0,
                },
                cls.partner1: {
                    cls.productA: 100,
                    cls.productB: 120,
                    cls.productC: 0,
                },
            },
        }

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_with_error(self):
        """Test the delivery of a sale order with customer deposit."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 50.0,
            self.productB: 70.0,
            self.productC: 90.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        so.order_line.route_id = self.warehouse.customer_deposit_route_id
        with self.assertRaises(
            ValidationError,
            msg="You can't use customer deposit for products with the route"
            " 'Customer Deposit'.",
        ):
            so.action_confirm()

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_sale_01(self):
        """Test the delivery of a sale order with partner 1 and product_uom_qty
        less than reserved quantities."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 50.0,
            self.productB: 70.0,
            self.productC: 90.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        so.action_confirm()
        # Check discount on lines
        self.assertTrue(
            sum(so.mapped("order_line.discount")) > 0.0,
            "Discount is not set properly on order lines",
        )
        for partner, products in self.result_test["sale1"].items():
            for product, value in products.items():
                self.assertEqual(
                    self.env["stock.quant"]._get_available_quantity(
                        product, self.warehouse.lot_stock_id, owner_id=partner
                    ),
                    value,
                )

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_sale_02(self):
        """Test the delivery of a sale order with partner 2 (child of partner 1)
        and product_uom_qty less than reserved quantities."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1_child
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 50.0,
            self.productB: 70.0,
            self.productC: 90.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        so.action_confirm()
        for partner, products in self.result_test["sale2"].items():
            for product, value in products.items():
                self.assertEqual(
                    self.env["stock.quant"]._get_available_quantity(
                        product, self.warehouse.lot_stock_id, owner_id=partner
                    ),
                    value,
                )

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_sale_03(self):
        """Test the delivery of a sale order with partner 3 and
        product_uom_qty less than reserved quantities."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner2
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 50.0,
            self.productB: 70.0,
            self.productC: 90.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        so.action_confirm()
        for partner, products in self.result_test["sale3"].items():
            for product, value in products.items():
                self.assertEqual(
                    self.env["stock.quant"]._get_available_quantity(
                        product, self.warehouse.lot_stock_id, owner_id=partner
                    ),
                    value,
                )

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_sale_04(self):
        """Test the delivery of a sale order with partner 1 and
        product_uom_qty more than reserved quantities."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 200.0,
            self.productB: 200.0,
            self.productC: 200.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        with self.assertRaises(
            ValidationError,
            msg="You can't add more than the quantity of Product A from the customer's"
            " deposit. If the customer wants more, create a new order after confirming this "
            "one.",
        ):
            so.action_confirm()

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_sale_05(self):
        """Test the delivery of a sale order with partner 2 (child of partner 1) and
        product_uom_qty more than reserved quantities."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1_child
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 200.0,
            self.productB: 200.0,
            self.productC: 200.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        with self.assertRaises(
            ValidationError,
            msg="You can't add more than the quantity of Product A from the "
            "customer's deposit. If the customer wants more, create a new order "
            "after confirming this one.",
        ):
            so.action_confirm()

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_sale_06(self):
        """Test the delivery of a sale order with partner 3 and
        product_uom_qty more than reserved quantities."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner2
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 200.0,
            self.productB: 200.0,
            self.productC: 200.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        so.action_confirm()
        for partner, products in self.result_test["sale6"].items():
            for product, value in products.items():
                self.assertEqual(
                    self.env["stock.quant"]._get_available_quantity(
                        product, self.warehouse.lot_stock_id, owner_id=partner
                    ),
                    value,
                )

    @users("user_customer_deposit")
    def test_deliver_customer_deposit_sale_07(self):
        """Test the delivery of a sale order with partner 3 and
        product_uom_qty more than quantities in stock."""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner2
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 500.0,
            self.productB: 600.0,
            self.productC: 700.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        so.action_confirm()
        for partner, products in self.result_test["sale7"].items():
            for product, value in products.items():
                self.assertEqual(
                    self.env["stock.quant"]._get_available_quantity(
                        product, self.warehouse.lot_stock_id, owner_id=partner
                    ),
                    value,
                )

    @users("user_customer_deposit")
    def test_actions(self):
        self.assertEqual(self.partner1.customer_deposit_count, 2)
        domain = self.partner1.action_view_customer_deposits()["domain"]
        quants_partner = self.env["stock.quant"].search(domain)
        self.assertRecordValues(
            quants_partner,
            [
                {
                    "product_id": self.productA.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "quantity": 100,
                    "owner_id": self.partner1.id,
                },
                {
                    "product_id": self.productB.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "quantity": 120,
                    "owner_id": self.partner1.id,
                },
            ],
        )
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1
        so_form.warehouse_id = self.warehouse
        with so_form.order_line.new() as line:
            line.product_id = self.productA
            line.product_uom_qty = 10.0
        so = so_form.save()
        self.assertEqual(so.customer_deposit_count, 2)
        domain = so.action_view_customer_deposits()["domain"]
        quants_partner = self.env["stock.quant"].search(domain)
        self.assertRecordValues(
            quants_partner,
            [
                {
                    "product_id": self.productA.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "quantity": 100,
                    "owner_id": self.partner1.id,
                },
                {
                    "product_id": self.productB.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "quantity": 120,
                    "owner_id": self.partner1.id,
                },
            ],
        )
        self.assertEqual(so.order_line[0].deposit_available_qty, 100)
        self.assertEqual(so.order_line[0].deposit_allowed_qty, 90)
        domain = so.order_line[0].action_view_customer_deposits()["domain"]
        quants_partner = self.env["stock.quant"].search(domain)
        self.assertRecordValues(
            quants_partner,
            [
                {
                    "product_id": self.productA.id,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "quantity": 100,
                    "owner_id": self.partner1.id,
                },
            ],
        )

# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form

from odoo.addons.stock_customer_deposit.tests.common import (
    TestStockCustomerDepositCommon,
)


class TestCustomeDepostiSaleMargin(TestStockCustomerDepositCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        (cls.productA | cls.productB | cls.productC).write({"standard_price": 10.0})
        stock_dict = {
            cls.productA: {cls.partner1: 100},
            cls.productB: {cls.partner1: 120},
            cls.productC: {False: 500},
        }
        cls.update_availiable_quantity(cls, stock_dict)

    def test_stock_customer_deposit_sale_margin(self):
        """Check purchase price is set to zero when make sale order to
        deliver customer deposit"""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1
        so_form.partner_id = self.partner1
        so_form.warehouse_id = self.warehouse
        product_qty_dict = {
            self.productA: 100.0,
            self.productB: 130.0,
            self.productC: 90.0,
        }
        for product, qty in product_qty_dict.items():
            with so_form.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = qty
        so = so_form.save()
        self.assertRecordValues(
            so.order_line.sorted(),
            [
                {"product_id": self.productA.id, "purchase_price": 0.0},
                {"product_id": self.productB.id, "purchase_price": 10.0},
                {"product_id": self.productC.id, "purchase_price": 10.0},
            ],
        )

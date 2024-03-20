# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form
from odoo.tests.common import users

from odoo.addons.stock_customer_deposit.tests.common import (
    TestStockCustomerDepositCommon,
)


class TestStockCustomerDepositElaboration(TestStockCustomerDepositCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.route_elaboration = cls.env["stock.route"].create(
            {"name": "Elaboration", "sale_selectable": "True"}
        )
        cls.product_elaboration_A = cls.env["product.product"].create(
            {
                "name": "Product Elaboration A",
                "type": "service",
                "list_price": 50.0,
                "invoice_policy": "order",
                "is_elaboration": True,
            }
        )
        cls.elaboration_a = cls.env["product.elaboration"].create(
            {
                "code": "AA",
                "name": "Elaboration A",
                "product_id": cls.product_elaboration_A.id,
                "route_ids": [(4, cls.route_elaboration.id)],
            }
        )

    @users("user_customer_deposit")
    def test_sale_customer_deposit_elaboration(self):
        """Test that the route of the sale order line is updated when the
        customer deposit is enabled or disabled and elaboration with route
        is set"""
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner1_child
        so_form.warehouse_id = self.warehouse
        so_form.customer_deposit = True
        with so_form.order_line.new() as line:
            line.product_id = self.productA
            line.product_uom_qty = 100.0
        with so_form.order_line.new() as line:
            line.product_id = self.productB
            line.product_uom_qty = 110.0
        so = so_form.save()
        self.assertRecordValues(
            so.order_line,
            [
                {
                    "route_id": self.warehouse.customer_deposit_route_id.id,
                },
                {
                    "route_id": self.warehouse.customer_deposit_route_id.id,
                },
            ],
        )
        so.order_line.write({"elaboration_ids": [(4, self.elaboration_a.id)]})
        self.assertRecordValues(
            so.order_line,
            [
                {
                    "route_id": self.warehouse.customer_deposit_route_id.id,
                },
                {
                    "route_id": self.warehouse.customer_deposit_route_id.id,
                },
            ],
        )
        so.customer_deposit = False
        self.assertRecordValues(
            so.order_line,
            [
                {
                    "route_id": self.route_elaboration.id,
                },
                {
                    "route_id": self.route_elaboration.id,
                },
            ],
        )
        so.order_line[1].write({"elaboration_ids": [(6, 0, [])]})
        self.assertRecordValues(
            so.order_line,
            [
                {
                    "route_id": self.route_elaboration.id,
                },
                {
                    "route_id": False,
                },
            ],
        )

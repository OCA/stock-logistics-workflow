# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import new_test_user

from odoo.addons.product.tests.common import ProductCommon
from odoo.addons.sales_team.tests.common import SalesTeamCommon


class TestStockCustomerDepositCommon(ProductCommon, SalesTeamCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_test_user(
            cls.env,
            login="stock_manager",
            groups="stock.group_stock_manager",
        )
        new_test_user(
            cls.env,
            login="user_customer_deposit",
            groups="sales_team.group_sale_salesman,stock.group_stock_user,"
            "stock.group_tracking_owner,stock.group_adv_location",
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TEST",
                "use_customer_deposits": True,
            }
        )
        cls.productA = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
            }
        )
        cls.productB = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
            }
        )
        cls.productC = cls.env["product.product"].create(
            {
                "name": "Product C",
                "type": "product",
            }
        )
        cls.partner1 = cls.env["res.partner"].create({"name": "Test Partner 1"})
        cls.partner1_child = cls.env["res.partner"].create(
            {"name": "Test Partner1 Child", "parent_id": cls.partner1.id}
        )
        cls.partner2 = cls.env["res.partner"].create({"name": "Test Partner3"})

    def update_availiable_quantity(self, stock_dict):
        for product, dict_values in stock_dict.items():
            for owner, value in dict_values.items():
                self.env["stock.quant"]._update_available_quantity(
                    product,
                    self.warehouse.lot_stock_id,
                    value,
                    owner_id=owner,
                )

# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class TestStockSaleProductVolume(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env["res.config.settings"].create(
            {"group_stock_packaging": True, "group_stock_tracking_lot": True},
        ).execute()
        self.package_type = self.env.ref("stock.package_type_01")
        self.partner_id = self.env.ref("base.res_partner_3")
        self.product_id = self.env.ref("product.product_product_25")
        self.product_packaging = self.env["product.packaging"].create(
            {
                "name": "Test packaging",
                "product_id": self.product_id.id,
                "package_type_id": self.package_type.id,
                "qty": 10,
                "company_id": self.product_id.company_id.id,
            }
        )

    def test_package_type_compute_volume(self):
        self.assertEqual(self.package_type.volume, 0.1248)

    def test_sale_order_compute_total_volume(self):
        order_id = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "product_packaging_qty": 1,
                            "product_packaging_id": self.product_packaging.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(order_id.total_volume, 0.1248)

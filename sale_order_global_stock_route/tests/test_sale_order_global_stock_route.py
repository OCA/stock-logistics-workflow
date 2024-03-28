# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class SaleOrderGlobalStockRouteTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product1 = cls.env["product.product"].create(
            {"name": "test_product1", "type": "product"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "test_product2", "type": "product"}
        )
        cls.route1 = cls.env["stock.route"].create(
            {"name": "test_route_1", "sale_selectable": "True"}
        )
        cls.route2 = cls.env["stock.route"].create(
            {"name": "test_route_2", "sale_selectable": "True"}
        )
        cls.order = cls.env["sale.order"].create(
            [
                {
                    "partner_id": cls.partner.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": cls.product1.name,
                                "product_id": cls.product1.id,
                                "product_uom_qty": 1,
                                "product_uom": cls.product1.uom_id.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": cls.product2.name,
                                "product_id": cls.product2.id,
                                "product_uom_qty": 1,
                                "product_uom": cls.product2.uom_id.id,
                            },
                        ),
                    ],
                },
            ]
        )

    def test_global_route(self):
        self.order["route_id"] = self.route1.id
        self.order._onchange_route_id()
        for line in self.order.order_line:
            self.assertTrue(line.route_id == self.route1)

    def test_global_route02(self):
        self.order["route_id"] = self.route1.id
        for line in self.order.order_line:
            line.global_stock_route_product_id_change()
            self.assertTrue(line.route_id == self.route1)

    def test_routes_without_onchange(self):
        new_order = self.env["sale.order"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": self.product1.name,
                                "product_id": self.product1.id,
                                "product_uom_qty": 1,
                                "product_uom": self.product1.uom_id.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": self.product2.name,
                                "product_id": self.product2.id,
                                "product_uom_qty": 1,
                                "product_uom": self.product2.uom_id.id,
                            },
                        ),
                    ],
                    "route_id": self.route1.id,
                },
            ]
        )
        for line in new_order.order_line:
            self.assertTrue(line.route_id == self.route1)
        new_order.order_line[0].route_id = self.route2
        new_order.write({})
        self.assertTrue(new_order.order_line[0].route_id == self.route2)
        new_order.write({"route_id": self.route2.id})
        for line in new_order.order_line:
            self.assertTrue(line.route_id == self.route2)

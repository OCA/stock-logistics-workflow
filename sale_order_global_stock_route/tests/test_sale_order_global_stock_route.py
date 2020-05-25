# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class SaleOrderGlobalStockRouteTest(TransactionCase):
    def setUp(self):
        super(SaleOrderGlobalStockRouteTest, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test',
        })
        self.product1 = self.env['product.product'].create({
            'name': 'test_product1',
            'type': 'product',
        })
        self.product2 = self.env['product.product'].create({
            'name': 'test_product2',
            'type': 'product',
        })
        self.route1 = self.env['stock.location.route'].create({
            'name': 'test_route_1',
            'sale_selectable': 'True',
        })
        self.route2 = self.env['stock.location.route'].create({
            'name': 'test_route_2',
            'sale_selectable': 'True',
        })
        self.order = self.env['sale.order'].create([{
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product1.name,
                    'product_id': self.product1.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product1.uom_id.id,
                }),
                (0, 0, {
                    'name': self.product2.name,
                    'product_id': self.product2.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product2.uom_id.id,
                })
            ],
        },
        ])

    def test_global_route(self):
        self.order['route_id'] = self.route1.id
        self.order._onchange_route_id()
        for line in self.order.order_line:
            self.assertTrue(line.route_id == self.route1)

    def test_global_route02(self):
        self.order['route_id'] = self.route1.id
        for line in self.order.order_line:
            line.product_id_change()
            self.assertTrue(line.route_id == self.route1)

    def test_routes_without_onchange(self):
        new_order = self.env['sale.order'].create([{
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product1.name,
                    'product_id': self.product1.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product1.uom_id.id,
                }),
                (0, 0, {
                    'name': self.product2.name,
                    'product_id': self.product2.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product2.uom_id.id,
                })
            ],
            'route_id': self.route1.id,
        },
        ])
        for line in new_order.order_line:
            self.assertTrue(line.route_id == self.route1)
        new_order.order_line[0].route_id = self.route2
        new_order.write({})
        self.assertTrue(new_order.order_line[0].route_id == self.route2)
        new_order.write({'route_id': self.route2.id})
        for line in new_order.order_line:
            self.assertTrue(line.route_id == self.route2)

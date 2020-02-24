# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from lxml import etree


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
        self.route = self.env['stock.location.route'].create({
            'name': 'test_route',
            'sale_selectable': 'True',
        })
        self.order = self.env['sale.order'].create({
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
            'route_id': self.route.id,
        })
        self.View = self.env['ir.ui.view']

    def _get_ctx_from_view(self, res):
        order_xml = etree.XML(res['arch'])
        order_line_path = "//field[@name='order_line']"
        order_line_field = order_xml.xpath(order_line_path)[0]
        return order_line_field.attrib.get('context', '{}')

    def test_global_route(self):
        self.order._onchange_route_id()
        for line in self.order.order_line:
            self.assertTrue(line.route_id == self.route)

    def test_default_line_route_id(self):
        res = self.order.fields_view_get(
            view_id=self.env.ref('sale_order_global_stock_route.'
                                 'view_order_form').id,
            view_type='form')
        ctx = self._get_ctx_from_view(res)
        self.assertTrue('default_route_id' in ctx)
        view = self.View.create({
            'name': "test",
            'type': "form",
            'model': 'sale.order',
            'arch': """
                <data>
                    <field name='order_line'
                        context="{'default_product_uom_qty': 3.0}">
                    </field>
                </data>
            """
        })
        res = self.order.fields_view_get(view_id=view.id, view_type='form')
        ctx = self._get_ctx_from_view(res)
        self.assertTrue('default_route_id' in ctx
                        and 'default_product_uom_qty' in ctx)

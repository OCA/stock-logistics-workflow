# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase


class TestStockPickingBackorderToSale(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockPickingBackorderToSale, cls).setUpClass()
        cls.pricelist = cls.env.ref('product.list0')
        cls.category = cls.env['product.category'].create({
            'name': 'Test category',
            'type': 'normal',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'categ_id': cls.category.id,
            'default_code': 'TESTPROD01',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_dest_id':
                cls.env.ref('stock.stock_location_customers').id,
            'move_lines': [
                (0, 0, {'name': 'move1',
                        'product_id': cls.product.id,
                        'product_uom': cls.product.uom_id.id,
                        'product_uom_qty': 5,
                        'location_id':
                            cls.env.ref('stock.stock_location_stock').id,
                        'location_dest_id':
                            cls.env.ref('stock.stock_location_customers').id,
                        }
                 ),
            ],
        })

    def test_create_sale_order(self):
        new_orders = self.picking.create_sale_order()
        line = new_orders.order_line[:1]
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.product_uom_qty, 5)

    def test_button_create_sale(self):
        res = self.picking.button_create_sale()
        self.assertIn('res_id', res)
        res = (self.picking | self.picking.copy()).button_create_sale()
        self.assertIn('domain', res)

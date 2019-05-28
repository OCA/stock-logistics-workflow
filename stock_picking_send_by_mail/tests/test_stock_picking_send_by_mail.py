# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestStockPickingSendByMail(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingSendByMail, cls).setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'Test category',
            'type': 'normal',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'categ_id': cls.category.id,
        })
        cls.picking = cls.env['stock.picking'].create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_dest_id':
                cls.env.ref('stock.stock_location_customers').id,
            'move_lines': [
                (0, 0, {'name': 'move1',
                        'product_id': cls.product.id,
                        'product_uom': cls.product.uom_id.id,
                        'location_id':
                            cls.env.ref('stock.stock_location_stock').id,
                        'location_dest_id':
                            cls.env.ref('stock.stock_location_customers').id,
                        }
                 ),
            ],
        })

    def test_send_mail(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        result = self.picking.action_picking_send()
        self.assertEqual(result['name'], 'Compose Email')

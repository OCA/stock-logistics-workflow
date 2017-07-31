# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOSC - Alfredo de la Fuente
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestStockPickingCustomerRef(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockPickingCustomerRef, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test stuff',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {'product_id': cls.product.id})],
        })
        cls.sale_order.with_context(show_sale=True).action_confirm()

    def test_stock_picking_customer_ref(self):
        self.sale_order.client_order_ref = 'EDIT123456'
        for picking in self.sale_order.picking_ids:
            self.assertEqual(
                picking.client_order_ref, self.sale_order.client_order_ref,
                'Order ref of picking not equal to client order ref in sale')
        self.sale_order.client_order_ref = 'AGAIN123456'
        for picking in self.sale_order.picking_ids:
            self.assertEqual(
                picking.client_order_ref, self.sale_order.client_order_ref,
                'Order ref of picking not equal to client order ref in sale')

    def test_stock_picking_customer_ref_on_sale_creation(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'client_order_ref': 'CREATE123456',
            'order_line': [(0, 0, {'product_id': self.product.id})],
        })
        sale_order.with_context(show_sale=True).action_confirm()
        for picking in sale_order.picking_ids:
            self.assertEqual(
                picking.client_order_ref, sale_order.client_order_ref,
                'Order ref of picking not equal to client order ref in sale')

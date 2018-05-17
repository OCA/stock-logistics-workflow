# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.stock_cancel.tests.test_stock_cancel import TestStockCancel


class TestStockCancelDelivery(TestStockCancel):

    @classmethod
    def setUpClass(cls):
        super(TestStockCancelDelivery, cls).setUpClass()

    def test_delete_delivery_line(self):
        so_vals = {
            'partner_id': self.partner.id,
            'carrier_id': self.env.ref('delivery.free_delivery_carrier').id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price})]
        }
        self.so = self.env['sale.order'].create(so_vals)
        self.so.action_confirm()
        # deliver completely
        picking = self.so.picking_ids
        picking.force_assign()
        picking.do_transfer()
        self.assertEqual(len(
            self.so.order_line), 2)
        picking.action_revert_done()
        self.assertEqual(len(
            self.so.order_line), 1, "sale delivery line not deleted")

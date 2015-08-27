# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp.exceptions import Warning


class TestStockCancel(common.TransactionCase):

    def setUp(self):
        super(TestStockCancel, self).setUp()
        self.picking_model = self.env['stock.picking']
        self.move_model = self.env['stock.move']
        self.product_model = self.env['product.product']
        self.partner_delta = self.env.ref('base.res_partner_4')
        self.picking_type_in = self.env.ref('stock.picking_type_in')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.product = self.product_model.create({'name': 'Product A'})
        self.picking_in = self.picking_model.create({
            'partner_id': self.partner_delta.id,
            'picking_type_id': self.picking_type_in.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 288,
                'product_uom': self.product.uom_id.id,
                'location_id': self.supplier_location.id,
                'location_dest_id': self.stock_location.id,
            })],
        })
        self.picking_in.action_confirm()
        self.picking_in.do_prepare_partial()
        self.picking_in.do_transfer()

    def test_transferred_stock_picking_cancel(self):
        self.assertEqual(self.picking_in.state, 'done')
        self.picking_in.action_revert_done()
        self.assertEqual(self.picking_in.state, 'draft')

    def test_stock_picking_cancel_errors(self):
        picking_out = self.picking_model.create({
            'partner_id': self.partner_delta.id,
            'picking_type_id': self.picking_type_out.id,
            'move_lines': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 10,
                'product_uom': self.product.uom_id.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
            })],
        })
        picking_out.action_confirm()
        picking_out.do_prepare_partial()
        picking_out.do_transfer()
        self.assertEqual(picking_out.state, 'done')
        with self.assertRaises(Warning):
            self.picking_in.action_revert_done()

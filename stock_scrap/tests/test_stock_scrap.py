# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestStockScrap(TransactionCase):

    def setUp(self):
        super(TestStockScrap, self).setUp()
        self.user_demo = self.env.ref('base.user_demo')
        self.scrap_obj = self.env['stock.scrap']
        self.picking_obj = self.env['stock.picking']
        self.stock_loc = self.browse_ref('stock.stock_location_stock')
        self.customer_loc = self.browse_ref('stock.stock_location_customers')
        self.product6 = self.env.ref('product.product_product_6')
        self._update_product_qty(self.product6)

    def _update_product_qty(self, product):
        product_qty = self.env['stock.change.product.qty'].create({
            'location_id': self.stock_loc.id,
            'product_id': product.id,
            'new_quantity': 100.0,
        })
        product_qty.change_product_qty()
        return product_qty

    def _prepare_picking(self):
        picking = self.picking_obj.create({
            'name': 'picking - test',
            'location_id': self.stock_loc.id,
            'location_dest_id': self.customer_loc.id,
            'picking_type_id': self.ref('stock.picking_type_out'),
            'move_lines': [(0, 0, {
                'name': self.product6.name,
                'product_id': self.product6.id,
                'product_uom_qty': 20.0,
                'product_uom': self.product6.uom_id.id,
            })]
        })
        return picking

    def test_stock_scrap_01(self):
        scrap = self.scrap_obj.create({
            'name': 'scrap - grand test',
            'product_id': self.product6.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
        })
        scrap.onchange_product_id()
        self.assertTrue(scrap.id)
        with self.assertRaises(UserError):
            scrap.sudo(self.user_demo).unlink()

    def test_stock_scrap_02(self):
        picking = self._prepare_picking()
        picking.action_assign()
        picking.do_transfer()
        scrap = self.scrap_obj.create({
            'name': 'scrap - grand test',
            'product_id': self.product6.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'picking_id': picking.id,
        })
        scrap._onchange_picking_id()
        scrap.action_get_stock_picking()
        scrap.action_get_stock_move()
        scrap.action_done()

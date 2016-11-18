# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError
from openerp.osv import osv


class TestPickingBackToDraft(TransactionCase):

    def _create_picking(self):
        stock_picking = self.env['stock.picking']
        res = stock_picking.onchange_picking_type(
            self.env.ref('stock.picking_type_out').id, self.partner.id)
        return stock_picking.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': res['value']['location_id'],
            'location_dest_id': res['value']['location_dest_id'],
        })

    def _create_move(self, picking, product, quantity=5.0):
        src_location = self.env.ref('stock.stock_location_stock')
        dest_location = self.env.ref('stock.stock_location_customers')
        return self.env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom': product.uom_id.id,
            'location_id': src_location.id,
            'location_dest_id': dest_location.id,
        })

    def setUp(self, *args, **kwargs):
        super(TestPickingBackToDraft, self).setUp(*args, **kwargs)
        self.partner = self.env.ref('base.res_partner_2')
        self.product1 = self.env.ref('product.product_product_33')
        self.product2 = self.env.ref('product.product_product_36')
        self.picking_a = self._create_picking()
        self.move_a_1 = self._create_move(
            self.picking_a, self.product1, quantity=1)
        self.move_a_2 = self._create_move(
            self.picking_a, self.product2, quantity=2)

    def test_back_to_draft(self):
        self.assertEqual(self.picking_a.state, 'draft')
        with self.assertRaises(UserError):
            self.picking_a.action_back_to_draft()
        self.picking_a.action_cancel()
        self.assertEqual(self.picking_a.state, 'cancel')
        self.picking_a.action_back_to_draft()
        self.assertEqual(self.picking_a.state, 'draft')
        self.picking_a.action_assign()
        self.assertEqual(self.picking_a.state, 'confirmed')
        with self.assertRaises(UserError):
            self.picking_a.action_back_to_draft()
        self.picking_a.action_cancel()
        self.assertEqual(self.picking_a.state, 'cancel')
        self.picking_a.action_back_to_draft()
        self.assertEqual(self.picking_a.state, 'draft')
        self.picking_a.action_confirm()
        self.assertEqual(self.picking_a.state, 'confirmed')
        self.picking_a.action_cancel()
        self.assertEqual(self.picking_a.state, 'cancel')
        self.picking_a.action_back_to_draft()
        self.assertEqual(self.picking_a.state, 'draft')
        self.picking_a.action_assign()
        self.assertEqual(self.picking_a.state, 'confirmed')
        self.picking_a.action_done()
        self.assertEqual(self.picking_a.state, 'done')
        with self.assertRaises(osv.except_osv):
            self.picking_a.action_cancel()
        with self.assertRaises(UserError):
            self.picking_a.action_back_to_draft()

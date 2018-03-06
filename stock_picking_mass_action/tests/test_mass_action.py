# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestMassAction(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMassAction, cls).setUpClass()

        partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
        product = cls.env['product.product'].create({
            'name': 'Product Test',
        })
        picking_type_out = cls.env.ref('stock.picking_type_out')
        stock_location = cls.env.ref('stock.stock_location_stock')
        customer_location = cls.env.ref('stock.stock_location_customers')
        inventory = cls.env['stock.inventory'].create({
            'name': 'Test Inventory',
            'filter': 'product',
            'product_id': product.id,
            'location_id': stock_location.id,
            'line_ids': [(0, 0, {
                'product_qty': 600,
                'location_id': stock_location.id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
            })],
        })
        inventory.action_done()
        # We create a picking out
        cls.picking = cls.env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': picking_type_out.id,
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id,
            'move_lines': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 200,
                'product_uom': product.uom_id.id,
                'location_id': stock_location.id,
                'location_dest_id': customer_location.id,
            })]
        })

    def test_mass_action(self):
        self.assertEqual(self.picking.state, 'draft')
        wiz = self.env['stock.picking.mass.action']
        # We test confirming a picking
        wiz_confirm = wiz.create({})
        wiz_confirm.confirm = True
        wiz_confirm.with_context(active_ids=[self.picking.id]).mass_action()
        self.assertEqual(self.picking.state, 'confirmed')
        # We test checking availability
        wiz_check = wiz.with_context(check_availability=True).create({})
        wiz_check.confirm = True
        wiz_check.with_context(active_ids=[self.picking.id]).mass_action()
        self.assertEqual(self.picking.state, 'assigned')
        # We test forcing availability
        self.picking.do_unreserve()
        wiz_force = wiz.with_context(force_availability=True).create({})
        wiz_force.confirm = True
        wiz_force.with_context(active_ids=[self.picking.id]).mass_action()
        self.assertEqual(self.picking.state, 'assigned')
        # We test transferring picking
        wiz_tranfer = wiz.with_context(transfer=True).create({})
        wiz_tranfer.confirm = True
        wiz_tranfer.with_context(active_ids=[self.picking.id]).mass_action()
        self.assertEqual(self.picking.state, 'done')
        # We test checking assign all
        pickings = self.env['stock.picking']
        pick1 = self.picking.copy()
        pickings |= pick1
        pick2 = self.picking.copy()
        pickings |= pick2
        self.assertEqual(pick1.state, 'draft')
        self.assertEqual(pick2.state, 'draft')
        wiz_confirm = wiz.create({})
        wiz_confirm.confirm = True
        wiz_confirm.with_context(active_ids=pickings.ids).mass_action()
        pickings.check_assign_all()
        self.assertEqual(pick1.state, 'assigned')
        self.assertEqual(pick2.state, 'assigned')

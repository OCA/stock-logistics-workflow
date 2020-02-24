# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestMassAction(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
        product = cls.env['product.product'].create({
            'name': 'Product Test',
            'type': 'product',
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
        inventory.action_validate()
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
        wiz_confirm = wiz.create({
            "picking_ids": [(4, self.picking.id)],
        })
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(self.picking.state, 'confirmed')
        # We test checking availability
        wiz_check = wiz.with_context(check_availability=True).create({
            "picking_ids": [(4, self.picking.id)],
        })
        wiz_check.confirm = True
        wiz_check.mass_action()
        self.assertEqual(self.picking.state, 'assigned')
        # We test transferring picking
        wiz_tranfer = wiz.with_context(transfer=True).create({
            "picking_ids": [(4, self.picking.id)],
        })
        wiz_tranfer.confirm = True
        for line in self.picking.move_lines:
            line.quantity_done = line.product_uom_qty
        wiz_tranfer.mass_action()
        self.assertEqual(self.picking.state, 'done')
        # We test checking assign all
        pickings = self.env['stock.picking']
        pick1 = self.picking.copy()
        pickings |= pick1
        pick2 = self.picking.copy()
        pickings |= pick2
        self.assertEqual(pick1.state, 'draft')
        self.assertEqual(pick2.state, 'draft')
        wiz_confirm = wiz.create({
            "picking_ids": [(6, 0, [pick1.id, pick2.id])],
        })
        wiz_confirm.confirm = True
        wiz_confirm.mass_action()
        self.assertEqual(pick1.state, 'confirmed')
        self.assertEqual(pick2.state, 'confirmed')
        pickings.check_assign_all()
        self.assertEqual(pick1.state, 'assigned')
        self.assertEqual(pick2.state, 'assigned')

    def test_mass_action_inmediate_transfer(self):
        wiz_tranfer = self.env['stock.picking.mass.action'].create({
            'picking_ids': [(4, self.picking.id)],
            'confirm': True,
            'transfer': True,
        })
        res = wiz_tranfer.mass_action()
        self.assertEqual(res['res_model'], 'stock.immediate.transfer')

    def test_mass_action_backorder(self):
        wiz_tranfer = self.env['stock.picking.mass.action'].create({
            'picking_ids': [(4, self.picking.id)],
            'confirm': True,
            'transfer': True,
        })
        self.picking.action_assign()
        self.picking.move_lines[0].quantity_done = 30
        res = wiz_tranfer.mass_action()
        self.assertEqual(res['res_model'], 'stock.backorder.confirmation')

    def test_mass_action_mixed_pikings(self):
        picking2 = self.picking.copy()
        wiz_tranfer = self.env['stock.picking.mass.action'].create({
            'picking_ids': [(4, self.picking.id), (4, picking2.id)],
            'confirm': True,
            'transfer': True,
        })
        self.picking.action_assign()
        self.picking.move_lines[0].quantity_done = 30
        res = wiz_tranfer.mass_action()
        self.assertEqual(res['res_model'], 'stock.backorder.confirmation')
        self.env[res['res_model']].browse(
            res['res_id']).process_cancel_backorder()
        self.assertEqual(self.picking.move_lines[0].state, 'done')
        self.assertEqual(picking2.move_lines[0].state, 'confirmed')

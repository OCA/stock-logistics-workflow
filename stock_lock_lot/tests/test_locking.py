# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.stock.tests.common import TestStockCommon
from openerp import exceptions


class TestLockingUnlocking(TestStockCommon):
    def setUp(self):
        super(TestLockingUnlocking, self).setUp()
        self.env['stock.config.settings']._write_or_create_param(
            'stock.lock.lot.strict', False)

        self.LotObj = self.env['stock.production.lot']

        #  Create a lot
        self.productA.type = 'product'
        self.lot = self.LotObj.create({'name': 'Test Lot',
                                       'product_id': self.productA.id})
        # Make sure we have this lot in stock
        inventory = self.InvObj.create({'name': 'Test Lot',
                                        'filter': 'product',
                                        'product_id': self.productA.id})
        inventory.prepare_inventory()
        self.InvLineObj.create({'inventory_id': inventory.id,
                                'product_id': self.productA.id,
                                'product_uom_id': self.productA.uom_id.id,
                                'product_qty': 10,
                                'location_id': self.stock_location,
                                'prod_lot_id': self.lot.id})
        inventory.action_done()

        # Record a picking
        self.picking_out = self.PickingObj.create(
            {'picking_type_id': self.picking_type_out})
        self.MoveObj.create(
            {'name': self.productA.name,
             'product_id': self.productA.id,
             'product_uom_qty': 5,
             'product_uom': self.productA.uom_id.id,
             'picking_id': self.picking_out.id,
             'location_id': self.stock_location,
             'location_dest_id': self.customer_location,
             'restrict_lot_id': self.lot.id})

        # Make an unauthorized user
        self.unauthorized_user = self.env["res.users"].create({
            "name": __file__,
            "login": __file__,
        })

    def test_lock(self):
        # Verify the button locks the lot
        self.lot.button_lock()
        # Verify unauthorized users can't unlock the lot
        with self.assertRaises(exceptions.Warning):
            self.lot.sudo(self.unauthorized_user).button_lock()
        self.assertTrue(self.lot.locked,
                        "The lot should be locked when the button is pressed")
        self.assertTrue(all([quant.locked for quant in self.lot.quant_ids]),
                        "All the quants should be locked when lot is locked")

        # Verify the lot isn't reserved automatically
        self.picking_out.action_assign()
        for move in self.picking_out.move_lines:
            self.assertNotEqual(
                move.state, 'assigned',
                "The stock move should not be assigned: the lot is locked."
                "Reserved lots: %s" % [(q.id, q.lot_id.name)
                                       for q in move.reserved_quant_ids])

    def test_unlock(self):
        self.lot.button_lock()
        # Verify unauthorized users can't unlock the lot
        with self.assertRaises(exceptions.Warning):
            self.lot.sudo(self.unauthorized_user).button_unlock()
        # Verify the button unlocks the lot when it's been locked
        self.lot.button_unlock()
        self.assertFalse(
            self.lot.locked,
            "The lot should be unlocked when the button is pressed")
        self.assertFalse(
            all([quant.locked for quant in self.lot.quant_ids]),
            "All the quants should be unlocked when lot is unlocked")

        # Verify the lot is reserved automatically
        self.picking_out.action_assign()
        for move in self.picking_out.move_lines:
            self.assertEqual(
                move.state, 'assigned',
                'The stock move should be assigned')

    def test_category_locked(self):
        self.productA.categ_id.lot_default_locked = True
        lot1 = self.LotObj.create({'name': 'Lot in locked category',
                                   'product_id': self.productA.id})
        self.assertTrue(lot1.locked, 'Category demands to lock new lots')

    def test_wizard(self):
        wizard = self.env['wiz.lock.lot'].with_context(
            active_ids=[self.lot.id])
        wizard.action_lock_lots()
        self.assertTrue(self.lot.locked, 'Wizard failed to lock the lot')

        wizard.action_unlock_lots()
        self.assertFalse(self.lot.locked, 'Wizard failed to unlock the lot')

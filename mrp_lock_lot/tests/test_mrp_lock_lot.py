# -*- coding: utf-8 -*-
# © 2016 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestMrpLockLot(common.TransactionCase):

    def setUp(self):
        super(TestMrpLockLot, self).setUp()
        self.production = self.env.ref('mrp.mrp_production_1')
        self.production.action_confirm()
        self.production.force_production()

    def test_not_allow(self):
        wizard = self.env['mrp.product.produce'].with_context(
            active_model='mrp.production', active_id=self.production.id,
            active_ids=[self.production.id]).create({})
        self.assertFalse(wizard.allow_locked)
        for line in wizard.consume_lines:
            self.assertFalse(line.allow_locked)

    def test_allow_consumed(self):
        self.production.product_id.property_stock_production.allow_locked = \
            True
        wizard = self.env['mrp.product.produce'].with_context(
            active_model='mrp.production', active_id=self.production.id,
            active_ids=[self.production.id]).create({})
        self.assertFalse(wizard.allow_locked)
        for line in wizard.consume_lines:
            self.assertTrue(line.allow_locked)

    def test_allow_produced(self):
        self.production.location_dest_id.allow_locked = True
        wizard = self.env['mrp.product.produce'].with_context(
            active_model='mrp.production', active_id=self.production.id,
            active_ids=[self.production.id]).create({})
        self.assertTrue(wizard.allow_locked)
        for line in wizard.consume_lines:
            self.assertFalse(line.allow_locked)

    def test_allow(self):
        self.production.product_id.property_stock_production.allow_locked = \
            True
        self.production.location_dest_id.allow_locked = True
        wizard = self.env['mrp.product.produce'].with_context(
            active_model='mrp.production', active_id=self.production.id,
            active_ids=[self.production.id]).create({})
        self.assertTrue(wizard.allow_locked)
        for line in wizard.consume_lines:
            self.assertTrue(line.allow_locked)

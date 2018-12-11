# -*- coding: utf-8 -*-
# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPartnerVersion(TransactionCase):

    def setUp(self):
        super(TestStockPartnerVersion, self).setUp()
        self.picking = self.env.ref('stock.outgoing_shipment_main_warehouse')

    def test_stock_version_partner(self):
        self.assertFalse(self.picking.partner_id.version_hash)
        self.picking.action_confirm()
        self.assertTrue(self.picking.partner_id.version_hash)

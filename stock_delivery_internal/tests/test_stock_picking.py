# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import TestCommon


class TestStockPicking(TestCommon):

    def test_creates_stock_pickup_request(self):
        """ It should create a pickup request when the carrier is assigned """
        self.picking_id.carrier_id = self.service_id
        self.picking_id.action_confirm()
        rfp = self.env['stock.pickup.request'].search([
            ('picking_id', '=', self.picking_id.id)
        ], limit=1)
        self.assertTrue(len(rfp) == 1)

# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import TestCommon


class TestStockPickupRequest(TestCommon):

    def _new_record(self):
        """ It creates a new `stock.pickup.request for testing """
        return self.env['stock.pickup.request'].create({
            'company_id': self.service_id.internal_delivery_company_id.id,
            'picking_id': self.picking_id.id,
        })

    def test_creates_pickings_on_create(self):
        """ It should create two pickings on create """
        obj = self._new_record()
        pickings = [obj.in_picking_id.id, obj.out_picking_id.id]
        self.assertTrue(all(pickings))

    def test_creates_cod_pickings(self):
        """ It should create pickings on CoD True"""
        obj = self._new_record()
        obj.cash_on_delivery = True
        pickings = [obj.cash_in_picking_id.id, obj.cash_in_picking_id.id]
        self.assertTrue(False not in pickings)
        self.assertEquals(
            obj.cash_out_picking_id.location_id.id,
            self.picking_id.location_id.id
        )

    def test_compute_state_new(self):
        """ It should default to new """
        obj = self._new_record()
        self.assertEquals(obj.state, 'new')

    def test_state_changes_with_pickings(self):
        obj = self._new_record()
        # Confirm the child pickings
        obj.in_picking_id.action_confirm()
        obj.out_picking_id.action_confirm()
        self.assertEquals(obj.state, 'confirmed')

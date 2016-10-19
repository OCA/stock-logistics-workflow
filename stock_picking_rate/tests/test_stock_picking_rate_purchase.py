# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestHelper


class TestStockPickingRate(TestHelper):

    def setUp(self):
        super(TestStockPickingRate, self).setUp()
        self.rate_ids = [self.new_record(), self.new_record()]
        self.Wizard = self.env['stock.picking.rate.purchase']
        self.wizard_vals = {
            'rate_ids': [(6, 0, [r.id for r in self.rate_ids])],
        }

    def new_wizard(self, vals=None):
        vals = self.wizard_vals if vals is None else {}
        return self.Wizard.create(vals)

    def test_default_rate_ids(self):
        """ It should default to active rate ids """
        expect = [r.id for r in self.rate_ids]
        rec_id = self.Wizard.with_context(
            active_ids=expect,
            active_model=self.Wizard._name,
        ).create()
        self.assertListEqual(
            expect, [r.id for r in rec_id.rate_ids]
        )

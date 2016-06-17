# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import TestHelper


class TestStockPickingDispatchRate(TestHelper):

    def test_compute_date_purchased(self):
        """ It should start out with no date, then have one after purchase """
        rec_id = self.new_record()
        self.assertFalse(rec_id.date_purchased)
        rec_id.write({
            'state': 'purchase',
        })
        self.assertTrue(rec_id.date_purchased)

    def test_compute_is_purchased_before(self):
        """ It should start out False """
        rec_id = self.new_record()
        self.assertFalse(rec_id.is_purchased)

    def test_compute_is_purchased_after(self):
        """ It should be True after purchase """
        rec_id = self.new_record()
        rec_id.write({
            'date_purchased': '2016-01-01 00:00:00',
        })
        self.assertTrue(rec_id.is_purchased)

    def test_name_get(self):
        """ It should return proper display_name & syntax """
        rec_id = self.new_record()
        expect = '{partner_name} {service_name} - {rate}'.format(
            partner_name=self.partner_id.name,
            service_name=self.service_id.name,
            rate=self.rate,
        )
        self.assertEqual(
            expect, rec_id.name_get()[0][1],
            'Did not get name w/ state. Expect %s, Got %s' % (
                expect, rec_id.name_get()[0][1],
            )
        )

    def test_action_purchase_calls_create(self):
        """ It should create new purchase wizard w/ rate """
        rec_id = self.new_record()
        with mock.patch.object(rec_id, 'env') as mk:
            model_mk = mk['stock.picking.dispatch.rate.purchase']
            rec_id.action_purchase()
            model_mk.create.assert_called_once_with(
                {'rate_ids': [(6, 0, [rec_id.id])]}
            )

    def test_action_purchase_returns_wizard_view(self):
        """ It should return result of wizard view helper """
        rec_id = self.new_record()
        with mock.patch.object(rec_id, 'env') as mk:
            model_mk = mk['stock.picking.dispatch.rate.purchase']
            res = rec_id.action_purchase()
            self.assertEqual(
                model_mk.create().action_show_wizard(),
                res,
            )

    def test_expire_other_rates_expires_rates(self):
        """ It should expire other rates associated with the same picking """
        rec_ids = [self.new_record(), self.new_record()]
        rec_ids[0]._expire_other_rates()
        self.assertEqual(
            'cancel', rec_ids[1].state,
        )

    def test_expire_other_rates_leaves_other_rate(self):
        """ It should not expire the rate it is called on """
        rec_ids = [self.new_record(), self.new_record()]
        rec_ids[0]._expire_other_rates()
        self.assertNotEqual(
            'cancel', rec_ids[0].state,
        )

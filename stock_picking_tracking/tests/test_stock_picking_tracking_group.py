# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from .common import TestHelper


class TestStockPickingTrackingGroup(TestHelper):

    def test_inherits_mail_thread(self):
        """ It should have properties provided by mail.thread inherit """
        model_obj = self.env['stock.picking.tracking.group']
        self.assertTrue(hasattr(model_obj, 'message_new'))

    def test_compute_last_event_id(self):
        """ It should set last_event_id to most recent event """
        group_id = self.new_group()
        event_ids = [self.new_event(group_id),
                     self.new_event(group_id),
                     self.new_event(group_id),
                     ]
        self.assertEqual(
            event_ids[-1], group_id.last_event_id,
        )

    def test_name_get_with_event(self):
        """ It should return proper display_name and syntax """
        rec_id = self.new_event()
        expect = '[{state}] {location}'.format(
            state=rec_id.state.capitalize(),
            location=rec_id.location_id.display_name,
        )
        self.assertEqual(
            expect, rec_id.group_id.name_get()[0][1],
            'Did not get name w/ state. Expect %s, Got %s' % (
                expect, rec_id.group_id.name_get()[0][1],
            )
        )

    def test_name_get_without_event(self):
        """ It should properly handle lack of events """
        rec_id = self.new_group()
        expect = '[{state}]'.format(
            state='UNKNOWN',
        )
        self.assertEqual(
            expect, rec_id.name_get()[0][1],
            'Did not get name w/ state. Expect %s, Got %s' % (
                expect, rec_id.name_get()[0][1],
            )
        )

    def test_name_get_with_tracking(self):
        """ It should include tracking in name_get if avail """
        rec_id = self.new_event()
        tracking = 'TRACKING'
        rec_id.group_id.ref = tracking
        expect = '[{state}] {location} - {tracking}'.format(
            state=rec_id.state.capitalize(),
            location=self.location_id.display_name,
            tracking=tracking,
        )
        self.assertEqual(
            expect, rec_id.group_id.name_get()[0][1],
            'Did not get name w/ state. Expect %s, Got %s' % (
                expect, rec_id.group_id.name_get()[0][1],
            )
        )

    def test_process_event_ensure_one(self):
        """ It should only allow operations on singleton """
        with self.assertRaises(ValueError):
            self.env['stock.picking.tracking.group']._process_event()

    def test_process_event(self):
        """ It should return values to create event """
        location_id = self.new_location()
        expect = {
            'message': 'MESSAGE',
            'state': 'delivered',
            'location_id': location_id,
            'date_created': '2016-01-23 00:00:00',
            'source': 'source',
        }
        group_id = self.new_group()
        res = group_id._process_event(**expect)
        expect.update({
            'group_id': group_id.id,
            'location_id': location_id.id,
        })
        self.assertDictEqual(
            expect, res,
        )

    def test_process_event_supports_int(self):
        """ It should return values to create event for int location """
        location_id = self.new_location()
        expect = {
            'message': 'MESSAGE',
            'state': 'delivered',
            'location_id': location_id.id,
            'date_created': '2016-01-23 00:00:00',
            'source': 'source',
        }
        group_id = self.new_group()
        res = group_id._process_event(**expect)
        expect.update({
            'group_id': group_id.id,
        })
        self.assertDictEqual(
            expect, res,
        )

    def test_create_event(self):
        """ It should create event with return of process method """
        group_id = self.new_group()
        location_id = self.new_location()
        with mock.patch.object(group_id, '_process_event') as mk:
            expect = {
                'message': u'MESSAGE',
                'state': u'delivered',
                'location_id': location_id.id,
                'date_created': '2016-01-23 00:00:00',
                'source': u'source',
                'group_id': group_id.id,
            }
            mk.return_value = expect
            res = group_id.create_event(**expect)
            res_eval = {}
            for key in expect.keys():
                attr = getattr(res, key, None)
                try:
                    res_eval[key] = attr.id
                except AttributeError:
                    res_eval[key] = attr
            self.assertDictEqual(
                expect, res_eval,
            )

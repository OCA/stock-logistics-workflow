# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestHelper


class TestStockPickingTrackingLocation(TestHelper):

    def test_name_get(self):
        """ It should return proper display_name and syntax """
        rec_id = self.new_event().location_id
        expect = '{city} {state} {zip}'.format(
            city=rec_id.city,
            state=rec_id.state_id.code,
            zip=rec_id.zip_code,
        )
        self.assertEqual(
            expect, rec_id.name_get()[0][1],
            'Did not get name w/ state. Expect %s, Got %s' % (
                expect, rec_id.name_get()[0][1],
            )
        )

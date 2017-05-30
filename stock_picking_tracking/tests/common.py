# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp.tests.common import TransactionCase


class TestHelper(TransactionCase):

    def setUp(self):
        super(TestHelper, self).setUp()
        self.picking_id = self.env['stock.picking'].create({
            'location_dest_id': self.env['stock.location'].search([])[0].id,
            'location_id': self.env['stock.location'].search([])[0].id,
            'picking_type_id':
                self.env['stock.picking.type'].search([])[0].id,
        })

    def new_group(self):
        return self.env['stock.picking.tracking.group'].create({
            'picking_id': self.picking_id.id,
        })

    def new_location(self):
        self.state_id = self.env['res.country.state'].browse(1)
        return self.env['stock.picking.tracking.location'].create({
            'city': 'Test City',
            'zip_code': '12345-6789',
            'state_id': self.state_id.id,
            'country_id': self.state_id.country_id.id,
        })

    def new_event(self, group_id=None):
        if group_id is None:
            group_id = self.new_group()
        self.location_id = self.new_location()
        return self.env['stock.picking.tracking.event'].create({
            'group_id': group_id.id,
            'location_id': self.location_id.id,
            'message': 'Test EVent',
        })

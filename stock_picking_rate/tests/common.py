# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        self.partner_id = self.env['res.partner'].create({'name': 'Carrier'})
        self.service_id = self.env['delivery.carrier'].create({
            'partner_id': self.partner_id.id,
            'name': 'Test Method',
        })
        self.rate = 1.23
        self.rate_vals = {
            'picking_id': self.picking_id.id,
            'service_id': self.service_id.id,
            'rate_currency_id': self.env.ref('base.USD').id,
            'rate': self.rate,
        }

    def new_record(self):
        return self.env['stock.picking.dispatch.rate'].create(self.rate_vals)

# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        location = self.env['stock.location'].search([])[0]
        self.partner_id = self.env['res.partner'].create({'name': 'Carrier'})
        self.picking_type = self.env['stock.picking.type'].search([])[0]
        self.picking_type.write({'default_location_src_id': location.id})

        self.product = self.env.ref('product.product_delivery_02')
        self.picking_id = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'location_dest_id': location.id,
            'location_id': location.id,
            'picking_type_id': self.picking_type.id,
            'move_lines': [[0, False, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'product_uom_qty': 1,
                'state': 'draft',
            }], [0, False, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'product_uom_qty': 1,
                'state': 'draft',
            }]],
        })
        self.service_id = self.env['delivery.carrier'].create({
            'name': 'Test Method',
            'delivery_type': 'internal',
            'internal_delivery_company_id':
                self.env['res.company'].search([])[0].id,
            'internal_delivery_stock_picking_type_id': self.picking_type.id,
            'internal_delivery_money_picking_type_id': self.picking_type.id
        })
        self.picking_id.carrier_id = self.service_id

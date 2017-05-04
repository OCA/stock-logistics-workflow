# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


OPERATION_STATES = [
    ('unknown', 'Unknown'),
    ('pre_transit', 'Pre Transit'),
    ('in_transit', 'In Transit'),
    ('out_for_delivery', 'Out For Delivery'),
    ('delivered', 'Delivered'),
    ('available_for_pickup', 'Available For Pickup'),
    ('return_to_sender', 'Return To Sender'),
    ('fail', 'Failure'),
    ('cancel', 'Cancelled'),
    ('error', 'Error'),
]


class StockPickingTrackingEvent(models.Model):
    _name = 'stock.picking.tracking.event'
    _description = 'Stock Picking Tracking Event'
    _order = "date_created desc"

    group_id = fields.Many2one(
        string='Tracking Group',
        comodel_name='stock.picking.tracking.group',
        required=True,
    )
    state = fields.Selection(
        OPERATION_STATES,
        required=True,
        default='unknown',
        help="Status of the dispatch at time of event",
    )
    date_created = fields.Datetime(
        string='Date',
        readonly=True,
        default=lambda s: fields.Datetime.now(),
    )
    location_id = fields.Many2one(
        string='Location',
        comodel_name='stock.picking.tracking.location',
        required=True,
    )
    message = fields.Char(
        required=True,
        help="Description of the tracking event",
    )
    source = fields.Char(
        help="Original source of the tracking event",
    )

    @api.multi
    def name_get(self):
        res = []
        for rec_id in self:
            name = '[{date}] {location} - {state}'.format(
                date=rec_id.date_created,
                location=rec_id.location_id.display_name,
                state=rec_id.state.capitalize(),
            )
            res.append((rec_id.id, name))
        return res

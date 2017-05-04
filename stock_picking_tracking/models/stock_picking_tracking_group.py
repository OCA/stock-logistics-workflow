# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
from .stock_picking_tracking_event import OPERATION_STATES


class StockPickingTrackingGroup(models.Model):
    _name = 'stock.picking.tracking.group'
    _description = 'Stock Picking Tracking Group'
    _order = 'date_created asc'
    _inherit = 'mail.thread'

    picking_id = fields.Many2one(
        string='Stock Picking',
        comodel_name='stock.picking',
        required=True,
    )
    ref = fields.Char()
    date_created = fields.Datetime(
        readonly=True,
        default=lambda s: fields.Datetime.now(),
    )
    date_updated = fields.Datetime(
        string='Date updated',
        readonly=True,
        related='last_event_id.date_created',
    )
    state = fields.Selection(
        OPERATION_STATES,
        related='last_event_id.state',
        default='unknown',
        readonly=True,
        help="Status of the dispatch at time of latest event",
    )
    location_id = fields.Many2one(
        string='Location',
        comodel_name='stock.picking.tracking.location',
        related='last_event_id.location_id',
        readonly=True,
    )
    event_ids = fields.One2many(
        string='Events',
        comodel_name='stock.picking.tracking.event',
        inverse_name='group_id',
    )
    last_event_id = fields.Many2one(
        string='Last Event',
        comodel_name='stock.picking.tracking.event',
        compute='_compute_last_event_id',
        readonly=True,
    )

    @api.multi
    @api.depends('event_ids')
    def _compute_last_event_id(self):
        for rec_id in self:
            if not len(rec_id.event_ids):
                continue
            rec_id.last_event_id = rec_id.event_ids.sorted(
                lambda r: r.date_created
            )[-1].id

    @api.multi
    def name_get(self):
        res = []
        for rec_id in self:
            try:
                state = rec_id.state.capitalize()
            except AttributeError:
                state = 'UNKNOWN'
            name = '[{state}]'.format(state=state)
            location = rec_id.location_id.display_name
            if location:
                name += ' {location}'.format(location=location)
            if rec_id.ref:
                name += ' - ' + rec_id.ref
            res.append((rec_id.id, name))
        return res

    @api.multi
    def _process_event(self, **kwargs):
        """ Receive & process event, handing back vals for creation

        Params:
            message: str describing event
            state: str indicating state that event represents
            location_id: stock.picking.tracking.location Record of event
            date_created: Date str of event, None for now
            source: str Source of event, usually carrier

        Returns:
            stock.picking.tracking.event Recordset of new events
        """
        self.ensure_one()
        location_id = kwargs.get('location_id', 0)
        try:
            location_id = location_id.id
        except AttributeError:
            pass
        return {
            'message': kwargs['message'],
            'state': kwargs.get('state', 'unknown'),
            'location_id': location_id,
            'date_created': kwargs.get('date_created'),
            'source': kwargs.get('source', 'Odoo'),
            'group_id': self.id,
        }

    @api.multi
    def create_event(self, message, state, location_id,
                     date_created=None, source=None, **kwargs
                     ):
        """ Create and return browse record of new events

        Params:
            message: str describing event
            state: str indicating state that event represents
            location_id: stock.picking.tracking.location Record of event
            date_created: Date str of event, None for now
            source: str Source of event, usually carrier

        Returns:
            stock.picking.tracking.event Recordset of new events
        """
        event_obj = self.env['stock.picking.tracking.event']
        res = event_obj.browse()
        for rec_id in self:
            res += event_obj.create(
                self._process_event(
                    message=message,
                    state=state,
                    location_id=location_id,
                    date_created=date_created,
                    source=source,
                    **kwargs
                )
            )
        return res

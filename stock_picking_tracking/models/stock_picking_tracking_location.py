# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class StockPickingTrackingLocation(models.Model):
    _name = 'stock.picking.tracking.location'
    _description = 'Stock Picking Tracking Location'

    event_ids = fields.One2many(
        string='Events',
        comodel_name='stock.picking.tracking.event',
        inverse_name='location_id',
    )
    city = fields.Char(required=True)
    zip = fields.Char(required=True)
    state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state',
        domain="[('country_id', '=', country_id)]",
        required=True,
    )
    country_id = fields.Many2one(
        string='Country',
        comodel_name='res.country',
        required=True,
    )

    @api.multi
    def name_get(self):
        res = []
        for rec_id in self:
            name = '{city} {state} {zip}'.format(
                city=rec_id.city,
                state=rec_id.state_id.code,
                zip=rec_id.zip,
            )
            res.append((rec_id.id, name))
        return res

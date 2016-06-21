# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockPickingTrackingLocation(models.Model):
    _name = 'stock.picking.tracking.location'
    _description = 'Stock Picking Tracking Location'

    event_ids = fields.One2many(
        string='Events',
        comodel_name='stock.picking.tracking.event',
        inverse_name='location_id',
    )
    city = fields.Char(required=True)
    zip_code = fields.Char(required=True)
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
        for record in self:
            name = '{city} {state} {zip_code}'.format(
                city=record.city,
                state=record.state_id.code,
                zip_code=record.zip_code,
            )
            res.append((record.id, name))
        return res

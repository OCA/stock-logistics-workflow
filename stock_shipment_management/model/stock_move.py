# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    departure_shipment_id = fields.Many2one(
        'shipment.plan', 'Departure shipment',
        readonly=True,
        copy=False
    )
    arrival_shipment_id = fields.Many2one(
        'shipment.plan', 'Arrival shipment',
        readonly=True,
        copy=False
    )

    @api.multi
    def write(self, values):
        res = super(StockMove, self).write(values)
        if values.get('state', '') == 'done':
            for ship in self.mapped('departure_shipment_id'):
                if ship.state == 'confirmed':
                    ship.signal_workflow('transit_start')
            for ship in self.mapped('arrival_shipment_id'):
                if ship.state == 'in_transit':
                    ship.signal_workflow('transit_end')
        return res

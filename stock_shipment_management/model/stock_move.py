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
#
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

    ship_carrier_id = fields.Many2one(
        related='departure_shipment_id.carrier_id',
        readonly=True,
        store=True
    )
    ship_carrier_tracking_ref = fields.Char(
        related='departure_shipment_id.carrier_tracking_ref',
        string='Tracking Ref.',
        readonly=True
    )
    ship_from_address_id = fields.Many2one(
        compute='_get_ship_addresses',
        comodel_name='res.partner',
        string='From Address',
        store=True
    )
    ship_to_address_id = fields.Many2one(
        compute='_get_ship_addresses',
        comodel_name='res.partner',
        string='To Address',
        store=True
    )
    ship_consignee_id = fields.Many2one(
        related='departure_shipment_id.consignee_id',
        string='Consignee',
        readonly=True,
    )
    ship_transport_mode_id = fields.Many2one(
        related='departure_shipment_id.transport_mode_id',
        string='Transport by',
        readonly=True,
    )
    ship_state = fields.Selection(
        related='departure_shipment_id.state',
        store=True,
    )

    @api.depends('picking_id.picking_type_id.code',
                 'picking_id.picking_type_id.warehouse_id.partner_id',
                 'picking_id.group_id.procurement_ids.purchase_id.partner_id')
    @api.one
    def _get_ship_addresses(self):
        picking = self.picking_id
        picking_type = picking.picking_type_id
        wh_address = picking_type.warehouse_id.partner_id
        if picking_type.code == 'outgoing':
            ref_dropship = 'stock_dropshipping.picking_type_dropship'
            if picking_type == self.env.ref(ref_dropship):
                self.ship_from_address_id = picking.group_id.mapped(
                    'procurement_ids.purchase_id.partner_id')
            else:
                self.ship_from_address_id = wh_address.id
            self.ship_to_address_id = picking.partner_id.id
        elif picking_type.code == 'incoming':
            self.ship_to_address_id = wh_address
            self.ship_from_address_id = picking.partner_id

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

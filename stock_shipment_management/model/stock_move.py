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
    ship_etd = fields.Datetime(
        related='date_expected',
        string='ETD',
        store=True
    )
    ship_eta = fields.Datetime(
        related='move_dest_id.date_expected',
        string='ETA',
        store=True
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

    @api.multi
    def _picking_assign(self, procurement_group, location_from, location_to):
        """ When an arrival transit move is split, we create a backorder

        """
        res = super(StockMove, self)._picking_assign(
            procurement_group, location_from, location_to)
        if self.env.context.get('split_transit_arrival') == 'arrival':
            context = {'do_only_split': True}
            Picking = self.env['stock.picking'].with_context(**context)
            Picking._create_backorder(self.picking_id, backorder_moves=self)
        return res

    @api.model
    def split(self, move, qty,
              restrict_lot_id=False, restrict_partner_id=False):
        """ Propagate the splitting of a departure transit move to
        its arrival transit move

        Here, we remove picking_id to force arrival move to trigger
        _picking_assign for new move

        """
        context = {}
        if move.departure_shipment_id:
            context['split_transit_arrival'] = 'departure'
        # On propagate split
        if self.env.context.get('split_transit_arrival') == 'departure':
            context['split_transit_arrival'] = 'arrival'

        _self = self.with_context(**context)
        res = super(StockMove, _self).split(
            move, qty,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id)
        return res

    @api.multi
    def copy(self, default=None):
        """ Ensure an arrival move from Transit is not assigned to same picking
        when source move is split

        """
        if default is None:
            default = {}
        if self.env.context.get('split_transit_arrival') == 'arrival':
            default['picking_id'] = False
        return super(StockMove, self).copy(default=default)

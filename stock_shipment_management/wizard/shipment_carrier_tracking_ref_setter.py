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
#    GNU Affero General Public License for more description.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import models, fields, api


class CarrierTrackingRefSetter(models.TransientModel):
    _name = "shipment.carrier_tracking_ref.setter"
    _inherit = "shipment.value.setter"

    carrier_tracking_ref = fields.Char(
        'Tracking Ref.',
    )

    @api.multi
    def set_value(self):
        """ Changes the Shipment ETA and update arrival moves """
        for setter in self:
            self.shipment_id.carrier_tracking_ref = self.carrier_tracking_ref
        pickings = self.shipment_id.departure_picking_ids
        pickings |= self.shipment_id.arrival_picking_ids
        pickings.write({'carrier_tracking_ref': self.carrier_tracking_ref})

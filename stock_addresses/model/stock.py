# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher, Alexandre Fayolle
#    Copyright 2014-2015 Camptocamp SA
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

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _picking_assign(self, procurement_group, location_from, location_to):
        _super = super(StockMove, self)
        res = _super._picking_assign(procurement_group,
                                     location_from,
                                     location_to)
        for picking in self.mapped('picking_id'):
            if not picking.group_id:
                continue
            changes = {}
            if not picking.consignee_id:
                changes['consignee_id'] = picking.group_id.consignee_id.id
            if not picking.delivery_address_id:
                changes['delivery_address_id'] = picking.group_id.partner_id.id
            if not picking.origin_address_id:
                changes['origin_address_id'] = picking.group_id.partner_id.id
            picking.write(changes)
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    consignee_id = fields.Many2one(
        'res.partner',
        'Consignee',
        help='The person to whom the shipment is to be delivered'
        )
    delivery_address_id = fields.Many2one(
        'res.partner',
        'Delivery Address',
        help='the delivery address of the shipment'
        )
    origin_address_id = fields.Many2one(
        'res.partner',
        'Origin Address',
        help='the origin address of the shipment'
        )

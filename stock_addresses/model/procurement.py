# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
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

from openerp import models, fields, api


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    consignee_id = fields.Many2one(
        'res.partner',
        'Consignee',
        help='The person to whom the shipment is to be delivered'
        )

    delivery_address_id = fields.Many2one(
        'res.partner',
        'Delivery Address',
        help='The final delivery address of the procurement group',
        )

    # this field is used for propagating the origin address in push rules,
    # where there is no information on the procurement.
    origin_address_id = fields.Many2one(
        'res.partner',
        'Origin Address',
        help='the origin address of the shipment'
        )


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    origin_address_id = fields.Many2one(
        'res.partner',
        'Origin Address',
        help='the origin address of the shipment'
        )

    consignee_id = fields.Many2one(
        related='group_id.consignee_id'
        )

    delivery_address_id = fields.Many2one(
        related='group_id.delivery_address_id'
        )

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        _super = super(ProcurementOrder, self)
        res = _super._prepare_orderpoint_procurement(orderpoint, product_qty)
        res.update({'partner_dest_id': orderpoint.warehouse_id.partner_id.id})
        return res

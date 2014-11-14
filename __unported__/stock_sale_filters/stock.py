# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
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

from openerp.osv.orm import Model
from openerp.osv import fields


class stock_picking(Model):
    _inherit = 'stock.picking'
    _columns = {
        'carrier_partner_id': fields.related('carrier_id', 'partner_id',
                                             type='many2one',
                                             relation='res.partner',
                                             string='Carrier Name',
                                             readonly=True,
                                             help="Name of the carrier partner"),
        'sale_shop_id': fields.related('sale_id', 'shop_id',
                                       type='many2one',
                                       relation='sale.shop',
                                       string='Shop',
                                       readonly=True,
                                       help='The shop from which the sale order for the picking was issued')
    }


class sale_order(Model):
    _inherit = 'sale.order'
    _columns = {
        'carrier_partner_id': fields.related('carrier_id', 'partner_id',
                                             type='many2one',
                                             relation='res.partner',
                                             string='Carrier Name',
                                             readonly=True,
                                             help="Name of the carrier partner")
    }

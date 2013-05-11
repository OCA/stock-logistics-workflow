# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2008 Raphaël Valyi
#    Copyright (C) 2013 Akretion (http://www.akretion.com/)
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

from osv import fields, osv

class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
        'lot_split_type': fields.selection([
            ('none','None'),
            ('single','Single'),
            ('lu','Logistical Unit')
            ], 'Lot split type', required=True,
            help="None: no split ; single: 1 line/product unit ; Logistical Unit: split using the first Logistical Unit quantity of the product form packaging tab (to be improved to take into account all LU)"),
    }

    _defaults = {
        'lot_split_type': 'none',
    }

product_product()


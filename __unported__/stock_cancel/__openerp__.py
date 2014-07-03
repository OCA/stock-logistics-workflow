# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    'name': 'Stock Cancel',
    'version': '1.2',
    'category': 'Stock',
    'description': """This module allows you to bring back a completed stock
picking to draft state""",
    'author': 'www.andreacometa.it',
    'website': 'http://www.andreacometa.it',
    'depends': ['stock_picking_invoice_link'],
    'data': [
        'stock_view.xml',
        ],
    'installable': False,
    'active': False,
    'images': ['images/stock_picking.jpg'],
}

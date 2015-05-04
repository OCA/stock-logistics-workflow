# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
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
{
    "name": "Stock Picking Deliver UOS",
    "version": "1.0",
    'author': ['Agile Business Group'],
    "category": "Stock Logistics",
    'website': 'www.agilebg.com',
    "depends": ["stock", "product", "base"],
    "summary": "Add fields uos and uos_quantity on Stock Partial Picking",
    "description": """This module adds two fields, uos and uos quantity on
    Stock Partial Picking wizard allowing the user to use the uos quantity
    (instead of the standard uom) to specify the quantity to be delivered.
    For example if i have to deliver 3 tables (uos qty=3 uos=pz)
    each one of 1,5 m² (uom=m², line uom qty=4,5),
    I can make a partial delivery specifying 2 pieces
    (the system computes the internal uom qty:  3 m²)""",
    'data': [
        "wizard/stock_partial_picking_view.xml",
    ],
    'test': ['test/stock_partial_picking.yml'],
    'demo': [],
    'installable': True,
}

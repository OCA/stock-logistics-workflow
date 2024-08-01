# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012+ BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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
    "name": "Stock Move Backdating",
    "version": "1.0",
    'author': ['Marco Dieckhoff, BREMSKERL', 'Agile Business Group'],
    "category": "Stock Logistics",
    'website': 'www.bremskerl.com',
    'license': 'AGPL-3',
    "depends": ["stock"],
    "summary": "Allows back-dating of stock moves",
    "description": """This module allows to register old stock moves
    (with date != now).
    On stock moves, user can specify the "Actual Movement Date", that will be
    used as movement date""",
    'data': [
        "view/stock_view.xml",
        "wizard/stock_partial_picking_view.xml",
    ],
    'demo': [],
    'installable': False,
}

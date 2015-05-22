# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl (<http://www.agilebg.com>)
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
    'author': "Agile Business Group, Odoo Community Association (OCA)",
    "category": "Stock Logistics",
    'website': 'www.agilebg.com',
    "depends": ["stock"],
    "summary": "Add fields uos and uos_quantity on Stock Transfer Details",
    'data': [
        "wizard/stock_transfer_details_view.xml",
    ],
    'test': ['test/stock_partial_picking.yml'],
    'demo': [],
    'installable': True,
}

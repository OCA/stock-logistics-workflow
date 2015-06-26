# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 AKRETION
#    @author Chafique Delli <chafique.delli@akretion.com>
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
    'name': 'Stock Meter Delay',
    'version': '0.1',
    'category': 'Warehouse Management',
    'license': 'AGPL-3',
    'summary': "",
    'description': """
    This module calculates the number of delivery order whose
    delivery date is close and display them.
    A parameter (warning time) was added to the company's configuration
    to define a number of days before which it is estimated
    that the delivery date is near.
    """,
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com/',
    'depends': [
        'stock',
        'sale_order_dates'
    ],
    'data': [
        'stock_view.xml',
        'company_view.xml',
    ],
    'installable': True,
}

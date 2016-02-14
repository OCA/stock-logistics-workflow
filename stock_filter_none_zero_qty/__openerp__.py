# -*- coding: utf-8 -*-
#############################################################################
#
#    Copyright (c) 2010-2012, OPENTIA Group (<http://opentia.com>)
#    The word "OPENTIA" is an European Community Trademark property
#    of the Opentia Group
#
#    @author: Opentia "Happy Hacking" Team
#    @e-mail: consultoria@opentia·es
#
#    This module is an improvement of the module "zero_stock_filter"
#    This is base on this module and improved by Julius Network Solutions
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
#############################################################################
{
    'name': 'Filter products in stock',
    'description': '''
       ·Adds a "Stock" button to product's search view to show
        stockable products with and without stock availability
       ·By default, only products with stock are shown (i.e.
        button is enabled)
       .This filter is applied on products view located in Warehouse menu.
       .Adds this filter from a location on button "More>Products"
        (via action window)
    ''',
    'version': '1.0',
    'depends': [
        "stock",
        "product",
    ],
    'category': 'Warehouse',
    'author': "OPENTIA,Odoo Community Association (OCA)",
    'contributors': 'Julius Network Solutions, Camptocamp',
    'website': 'http://www.opentia.com/, http://www.julius.fr/',
    'license': 'AGPL-3',
    'demo': [],
    'data': [
        'product_view.xml',
    ],
    'installable': False,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

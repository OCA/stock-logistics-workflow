# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author: Moisés Lopez, Osval Reyes
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
    'name': "Product Serial Unique Number",
    'version': '8.0.1.0.1',
    'author': "Vauxoo,Odoo Community Association (OCA)",
    'website': "http://www.vauxoo.com",
    'category': 'stock',
    'license': 'AGPL-3',
    'depends': [
        'stock_no_negative'
    ],
    'data': [
        "views/product_template.xml",
        "views/stock_production_lot.xml",
    ],
    'demo': [
        "demo/product_product.xml",
        "demo/stock_production_lot.xml",
    ],
    'installable': True,
    'auto_install': False,
}

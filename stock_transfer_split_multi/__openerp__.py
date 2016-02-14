# -*- encoding: utf-8 -*-
##############################################################################
#
#    Stock Transfer Split Multi module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Stock Transfer Split Multi',
    'version': '8.0.1.0.0',
    'category': 'Warehouse Management',
    'license': 'AGPL-3',
    'summary': "In the stock transfer wizard, you can split by multiple units",
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'data': [
        'wizard/stock_transfer_split_multi.xml',
        'wizard/stock_transfer_details.xml',
        ],
    'installable': True,
}

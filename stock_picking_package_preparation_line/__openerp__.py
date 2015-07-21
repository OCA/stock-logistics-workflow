# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
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
    'name': 'Stock Picking Package Preparation Line',
    'version': '1.0',
    'author': 'Apulia Software srl,Odoo Community Association (OCA)',
    'maintainer': 'Apulia Software srl',
    'license': 'AGPL-3',
    'category': 'Warehouse Management',
    'depends': [
        'stock_picking_package_preparation',
     ],
    'website': 'http://www.apuliasoftware.it',
    'data': [
        'view/stock_picking_package_preparation_line.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
 }

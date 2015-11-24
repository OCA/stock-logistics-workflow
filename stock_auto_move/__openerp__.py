# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 NDP Systèmes (<http://www.ndp-systemes.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

{
    'name': 'Automatic Move Processing',
    'version': '8.0.1.0.0',
    'author': 'NDP Systèmes, Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'website': 'http://www.ndp-systemes.fr',
    'depends': ['stock'],
    'data': [
        'data/stock_auto_move_data.xml',
        'views/stock_auto_move_view.xml',
    ],
    'demo': [
        'demo/stock_auto_move_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}

# -*- coding: utf8 -*-
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
    'version': '0.1',
    'author': 'NDP Systèmes',
    'maintainer': 'NDP Systèmes',
    'category': 'Warehouse',
    'depends': ['stock'],
    'description': """
Automatic Move Processing
=========================
This modules adds the possibility to have move automatically processed as soon as the products are available in the
move source location.

It also adds the possibility to define the move as being automatic in a procurement rule.

Automatic moves are triggered by previous move when the move is chained or by the scheduler otherwise.

Note that automatic moves are given a procurement group name "Automatic", whatever the user or the procurement rule
selects.
""",
    'website': 'http://www.ndp-systemes.fr',
    'data': [
        'stock_auto_move_data.xml',
        'stock_auto_move_view.xml',
    ],
    'demo': [
        'stock_auto_move_demo.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}


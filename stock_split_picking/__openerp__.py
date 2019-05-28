# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi, Guewen Baconnier, Yannick Vaucher
#    Copyright 2013-2015 Camptocamp SA
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
#
{'name': 'Split picking',
 'summary': 'Split a picking in two unconfirmed pickings',
 'version': '8.0.1.1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Warehouse Management',
 'complexity': "normal",  # easy, normal, expert
 'depends': ['stock'],
 'website': 'http://www.camptocamp.com',
 'data': ['view/stock_partial_picking.xml'],
 'demo': [],
 'test': ['test/test_picking_split.yml',
          'test/test_assigned_picking_split.yml',
          'test/test_picking_split_two_move_lines.yml'],
 'installable': True,
 'auto_install': False,
 }

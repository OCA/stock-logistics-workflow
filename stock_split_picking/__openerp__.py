# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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
{'name': 'Stock picking no confirm split',
 'version': 'version',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'stock',
 'complexity': "normal",  # easy, normal, expert
 'depends': ['stock'],
 'description': """
Split picking without delivery
------------------------------

This addon adds a "Split" button on the out picking form header.

It works like the classical picking split (when you deliver) but does not pass
 the backorder and backorder lines to state "done".
""",
 'website': 'http://www.camptocamp.com',
 'data': ['view/stock_partial_picking.xml'],
 'demo': [],
 'test': ['test/test_picking_split.yml'],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 }

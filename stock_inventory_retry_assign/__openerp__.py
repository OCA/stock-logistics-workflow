# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2014 Camptocamp SA
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

{'name': 'Check Availability after Inventories',
 'version': '1.0',
 'depends': ['stock',
             'procurement',
             ],
 'author': "Camptocamp",
 'description': """
Check again availability of delivery orders after inventories
=============================================================

When an inventory is done, available delivery orders stay available even if
after inventory the quantities are insufficient.

With this module, when an inventory is done, all the delivery orders
that are currently available with products in the inventory will be
checked again.

 """,
 'license': 'AGPL-3',
 'website': 'http://www.camptocamp.com',
 'category': 'Warehouse Management',
 'data': [],
 'test': ['test/test_inventory_done.yml',
          ],
 'installable': True,
 }

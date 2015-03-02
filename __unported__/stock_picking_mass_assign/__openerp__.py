# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

{'name': 'Delivery Orders Mass Assign',
 'version': '0.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'license': 'AGPL-3',
 'category': 'Warehouse Management',
 'depends': ['stock',
             ],
 'description': """
Delivery Orders Mass Assign
===========================

Facilities to check the availability of delivery orders:

* A wizard which allows to check availability on multiple delivery
  orders at a time.
* A scheduled action to check availability of all the delivery orders.
  It is not active by default.

This may be necessary for those who want to check the availability
more often than running the procurement scheduler.

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['wizard/check_assign_all_view.xml',
          'cron_data.xml',
          ],
 "test": ['test/test_check_assign_all.yml',
          ],
 'installable': False,
 'auto_install': False,
 }

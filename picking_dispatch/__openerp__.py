# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
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
{'name': 'Picking dispatch',
 'version': '1.2.3',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'complexity': "normal",  # easy, normal, expert
 'depends': ['stock',
             'base',
             'report_webkit',
             'base_headers_webkit',
             ],
 'description': """
Picking dispatch
================

This module allows you to group various picking into a dispatch order
(picking wave), having all the related moves in it and assigned to a warehouse
keeper.

Wave picking is an application of short interval scheduling, to assign orders
into groupings (waves) and release them together so as to allow management to
coordinate the several parallel and sequential activities required to complete
the work.

The individual orders in the wave are dependent on the criteria used to make
the selection. To organize the sequence of orders and assignment to waves,
consistent with routing, loading and planned departure times of shipping
vehicles or production requirements, etc., to reduce the space required for
shipping dock handling to assemble orders and load; and To assign staff to
each wave and function within a wave, with the expectation that all the work
assigned to each wave will be completed within the wave period.

From there, you can perform various operation :

 * Check availability of related moves and picking
 * Organize your deliveries by grouping on interesting matter (e.g. by
     transporter, by type of goods, etc..)
 * Make partial delivery
 * Print a report to pick the proper goods at once


 """,
 'website': 'http://www.camptocamp.com/',
 'data': ['picking_dispatch_view.xml',
          'picking_dispatch_sequence.xml',
          'wizard/create_dispatch_view.xml',
          'wizard/dispatch_assign_picker_view.xml',
          'wizard/dispatch_start_view.xml',
          'wizard/check_assign_all_view.xml',
          'report.xml',
          'cron_data.xml',
          'security/ir.model.access.csv',
          'security/security.xml',
          # 'picking_dispatch_workflow.xml',
          ],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False
 }

# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Picking Invoice Link",
    'version': '0.1',
    'category': 'Warehouse Management',
    'description': """
This module adds a link between pickings and generated invoices. So that user can easly reach the invoice related to the picking.

""",
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['stock'],
    "init_xml": [],
    "update_xml": [
        "stock_view.xml",
    ],
    "demo_xml": [],
    'tests': [
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}

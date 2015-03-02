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
    'version': '0.2',
    'category': 'Warehouse Management',
    'summary': 'Adds link between pickings and generated invoices',
    'description': """
This module adds a link between pickings and generated invoices.
So that user can easly reach the invoice related to the picking
and see the pickings related to the invoice. This only applies
on the invoices generated from pickings.

Authors
=======
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alexis de Lattre <alexis.delattre@akretion.com>
""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['stock_account'],
    "data": [
        "stock_view.xml",
        "account_invoice_view.xml",
    ],
    "demo": [],
    'test': [],
    'installable': True,
}

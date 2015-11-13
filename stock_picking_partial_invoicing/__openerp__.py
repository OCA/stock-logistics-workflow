# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
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
    'name': 'Stock picking partial invoicing',
    'version': '1.0',
    'category': 'Warehouse Management',
    'summary': 'In the stock invoice wizard, you can create invoices for '
               'partial quantities',
    'author': 'Eficent,Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    'depends': ['stock_account'],
    'data': [
        'wizard/stock_invoice_onshipping.xml',
        'views/stock_view.xml',
        'views/account_invoice_view.xml'
    ],
    'test': ['test/incoming_shipment_partial_invoice.yml'],
    "installable": True
}

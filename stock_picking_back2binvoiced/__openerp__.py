# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2015 Akretion
#    @author Florian da Costa <florian.dacosta@akretion.com>
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
###############################################################################


{
    'name': 'Stock Picking Back2Invoiced',
    'version': '0.1',
    'author': "Akretion,Odoo Community Association (OCA)",
    'category': 'Warehouse Management',
    'depends': [
        'stock_picking_invoice_link',
    ],
    'summary': 'Put the picking back to 2binvoiced state',
    'website': 'http://www.akretion.com/',
    'description': """
Stock Picking Back2Invoiced
===========================
If an invoice is created from a picking, when you delete it, the picking
will be back to '2binvoiced' state. So you will be able to generate a
new invoice.

Contributors
------------
* Florian da Costa <florian.dacosta@akretion.com>

""",
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

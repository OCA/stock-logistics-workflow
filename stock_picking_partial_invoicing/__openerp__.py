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
    'name': "Stock picking partial invoicing",
    'version': '1.0',
    'category': 'Warehouse Management',
    'description': """
Stock picking partial invoicing
===============================

This module was written to extend the invoicing capabilities of Odoo,
and allows users to create customer or supplier invoices for part of
a delivered Order or received Incoming Shipment.


Installation
============

No additional installation instructions are required.


Configuration
=============

This module does not require any additional configuration.

Usage
=====

When the user wants to create an invoice for a Delivery Order or
Incoming Shipment she/he can indicate which moves should be invoiced,
and what quantity to invoice.

Known issues / Roadmap
======================

This module conflicts with module 'stock_picking_invoice_link' available in
the same OCA repository.

Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
""",
    'author': "Eficent,Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['stock'],
    "data": [
        'wizard/stock_invoice_onshipping.xml',
        'view/stock.xml',


    ],
    'test': ['test/incoming_shipment_partial_invoice.yml'],
    "demo": [],
    "active": False,
    "installable": True
}

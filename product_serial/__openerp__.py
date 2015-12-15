# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2008 Raphaël Valyi
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com/)
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

{
    "name": "Product Serial",
    "summary": "Enhance Serial Number management",
    "version": "8.0.1.0.0",
    "author": "Akretion,NaN·tic,Odoo Community Association (OCA)",
    "website": "http://www.akretion.com",
    "depends": ["stock"],
    "category": "Inventory, Logistic, Storage",
    "license": "AGPL-3",
    "description": """Enhance the management of Production Lots (Serial Numbers) in Odoo.

Here are the additional features proposed by this module:

1. Add a new selection field 'Lot split type' on the product form
   under the 'Inventory' tab to specify how the Production Lots should be
   split on the Pickings.

2. Add a new wizard *Spread Serial Numbers* on the Transfer wizard of pickings
    """,
    "demo": ["product_demo.xml"],
    "data": [
        "product_view.xml",
        "wizard/prodlot_wizard_view.xml",
    ],
    'installable': True,
}

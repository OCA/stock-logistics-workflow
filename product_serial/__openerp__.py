# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2008 Raphaël Valyi
#    Copyright (C) 2013 Akretion (http://www.akretion.com/)
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
    "version": "1.0",
    "author": "Akretion, NaN·tic",
    "website": "http://www.akretion.com",
    "depends": ["stock"],
    "category": "Generic Modules/Inventory Control",
    "license": "AGPL-3",
    "description": """Enhance the management of Production Lots (Serial Numbers) in OpenERP.

Here are the additional features proposed by this module:

1. Add a new selection field 'Lot split type' on the product form
   under the 'Inventory' tab to specify how the Production Lots should be
   split on the Pickings (you should also enable 'Track Incoming/Outgoing
   Lots', and the new 'Track internal lots' field).

2. If the option 'Active auto split' is active for the Company,
   OpenERP will automagically split up picking list movements into one
   movement per product instance or logistical unit packing quantity (in
   that case, only the first logistical unit is taken into account at the
   present time. Improvement to take them all to be done!).

3. Turn Incoming Pickings into an editable grid where you can
   directly type the codes of a new production lot and/or tracking number
   to create and associate to the move (it also checks it doesn't exist
   yet).

4. If the option 'Group invoice lines' is active for the Company,
   OpenERP will group the invoice lines to make it look like the
   Sale/Purchase Order when generating an Invoice from a Picking.
    """,
    "demo": ["product_demo.xml"],
    "data": [
        "product_view.xml",
        "company_view.xml",
        "stock_view.xml",
        "wizard/prodlot_wizard_view.xml",
    ],
    "active": False,
    "installable": True
}

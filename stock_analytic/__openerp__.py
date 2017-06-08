# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    "name": "Stock analytic",
    "summary": "Adds an analytic account in stock move",
    "version": "1.0",
    "author": "Julius Network Solutions,"
    "ClearCorp, Odoo Community Association (OCA)",
    "website": "http://www.julius.fr/",
    'complexity': "easy",
    "category": "Warehouse Management",
    "depends": [
        "base",
        "stock",
        "sale",
        "purchase",
        "analytic",
        "sale_stock",
    ],
    "data": [
        "stock_view.xml",
    ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

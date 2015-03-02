# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-Guillaume, Matthieu Dietrich
#    Copyright 2008-2015 Camptocamp SA
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
    "name": "Stock obsolete",
    "summary": "Add product depreciation",
    "version": "1.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "category": "Generic Modules/Stock",
    "description":
    """
        Add a special view and wizard on product to check the validity of each
        stock product, with an amount of depreciation. Your finance can now
        take in charge a factor for each product, based on the depreciation
        value for each product. You can set the depreciation value based on the
        out of stock amount for each product for the last 12/24 months.
        Important: this module does not offer a way to change
        product depreciation.
    """,
    "website": "http://camptocamp.com",
    "depends": ["stock", "product"],
    "demo": [],
    "data": [
        "stock_obsolete_view.xml",
        "stock_obsolete_report.xml",
    ],
    'test': [
        'test/stock_obsolete.yml',
    ],
    "active": False,
    "installable": True
}

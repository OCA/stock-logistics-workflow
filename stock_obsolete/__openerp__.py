# -*- coding: utf-8 -*-
##############################################################################
#
# @author Grand-Guillaume Joel, Matthieu Dietrich
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name": "Stock obsolete",
    "version": "1.0",
    "author": "Camptocamp",
    "category": "Generic Modules/Stock",
    "module":
    """
        Add a special view and wizard on product to check the validity of each
        stock product, with an amount of depreciation. Your finance can now
        take in charge a factor for each product, based on the depreciation
        value for each product. You can set the depreciation value based on the
        out of stock amount for each product for the last 12/24 months.
    """,
    "website": "http://camptocamp.com",
    "depends": ["stock", "product"],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        "stock_obsolete_view.xml",
        "stock_obsolete_report.xml",
    ],
    'test': [
        'test/stock_obsolete.yml',
    ],
    "active": False,
    "installable": True
}

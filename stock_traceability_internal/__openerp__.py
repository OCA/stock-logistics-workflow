# -*- coding: utf-8 -*-
#
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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
#

{
    "name": "Enforce internal traceability",
    "version": "1.0",
    "depends": ["stock"],
    "author": u"Numérigraphe",
    "category": "Warehouse Management",
    "description": """
Enforce Serial Number traceability in Internal Moves
====================================================
This module makes adds a checkbox on the product form to indicate that internal
traceability is required for the produce.
When the box is check, the Serial Number will be mandatory for all Internal
Moves.""",
    "data": [
        "product_view.xml",
    ],
}

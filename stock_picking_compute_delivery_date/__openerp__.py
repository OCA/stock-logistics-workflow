# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
{"name": "Stock Picking Compute Delivery Date",
 "version": "1.0",
 "author": "Camptocamp",
 "category": 'Warehouse Management',
 "website": "http://camptocamp.com",
 "description": """
Stock Picking Compute Delivery Date
===================================

Features:

*

    """,
 "complexity": "normal",
 "depends": [
     "sale_stock",
     "stock",
 ],
 "data": [
     'wizard/by_product.xml',
     'data/cron.xml',
 ],
 "test": [
     'test/setup_user.yml',
     'test/test_mts_1.yml',
     'test/test_mts_2.yml',
     'test/test_mto.yml',
 ],
 "installable": True,
 }

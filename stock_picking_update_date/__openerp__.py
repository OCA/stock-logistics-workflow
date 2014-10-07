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
{"name": "Stock Picking Update Date",
 "version": "1.0",
 "author": "Camptocamp",
 "category": 'Warehouse Management',
 "website": "http://camptocamp.com",
 "description": """
Stock Picking Update Date
=========================

This module modifies the Picking object so that the "Scheduled Time" field is
replaced by a similar one that can be modified. If that is done, the scheduled
dates of the Moves in the Picking will be updated to get the same value.

As for the original field, if the moves have different scheduled dates, the
oldest one is taken.

The same modification is done in incoming, internal and outcoming pickings.

Two existing fields min_date and max_date are left unchanged, because they are
used in the core stock module when a picking is moved on the calendar view.
    """,
 "complexity": "normal",
 "depends": ["stock"],
 "data": ['view/picking.xml'],
 "test": [
     'test/setup_user.yml',
     'test/test_picking_internal.yml',
     'test/test_picking_in.yml',
     'test/test_picking_out.yml',
 ],
 "installable": True,
 }

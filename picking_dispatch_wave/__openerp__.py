# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Romain Deheele
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


{
    "name": "Picking Dispatch Wave",
    "version": "0.1",
    "depends": ['picking_dispatch', 'sale_stock'],
    "author": "Camptocamp",
    'license': 'AGPL-3',
    "description": """Allows to set a picking dispatch
including the number maximum of pickings that you want to pick:

* The picker sets a number n of pickings to do.

* The wizard will select moves from n pickings with oldest min_date.

* A picking dispatch is created with found moves

It's sort of basic wave picking.
""",
    "website": "http://www.camptocamp.com",
    "category": "Warehouse Management",
    "demo": [],
    "data": ['dispatch_wave_view.xml'],
    "test": ['test/test_dispatch_wave.yml'],
    "installable": True,
}

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
    "name": "Picking Dispatch picking-oriented",
    "version": "0.1",
    "depends": ['picking_dispatch','delivery'],
    "author": "Camptocamp",
    "license": "AGPL-3",
    "description": """picking_dispatch addon is stock move-oriented.
This addon changes it for a picking-oriented use.

On "Done" button, a wizard is displayed (same as picking_dispatch), but:

* moves are not passed to "done" state, but split between picked quantity and remains.

* unpicked moves are moved in a new backorder.

Then, when the picking dispatch state is done:

* the picking dispatch hides the "Stock Moves" tab, the user uses "Related Picking" tab to deliver pickings one after the other.

* the "Transfer Products" wizard ("Deliver" button) displays only moves linked to a done picking dispatch.

* on "Transfer Products" wizard, a carrier field is displayed to give possility to check and change it if it's necessary.
    """,
    "website": "http://www.camptocamp.com",
    "category": "Warehouse Management",
    "demo": [],
    "data": ['dispatch_view.xml'],
    "test": ['test/dispatch_picking_oriented.yml'],
    "installable": True,
}

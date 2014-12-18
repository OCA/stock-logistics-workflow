# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayollle
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
    "name": "stock routes transit ",
    "version": "0.1",
    "depends": ["stock"],
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Generic Modules/Stock",
    "installable": True,
    "data": ["view/stock_warehouse.xml",
             "data/stock_location.xml",
             "security/groups.xml",
             ],
    "test": ["test/stock_users.yml",
             "test/create_warehouse.yml",
             ],
}

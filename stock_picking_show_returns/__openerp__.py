# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name" : "Show returns on stock pickings",
    "version" : "1.0",
    "author" : "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category" : "Warehouse Management",
    "description" : """
    Show in pickings one tab that contains returns made for that picking.
    """,
    "website" : "www.serviciosbaeza.com",
    "license" : "AGPL-3",
    "depends" : [
        "stock",
    ],
    "demo" : [],
    "data" : [
        'stock_picking_view.xml',
    ],
    "installable" : True,
    "active" : False,
}

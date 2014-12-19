# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
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
	"name" : "SO related filters on stock.picking and sale.order",
	"version" : "1.3",
	"depends" : ["delivery"],
	"author" : "Camptocamp",
        "license": "AGPL-3",
	"description": """add filters on stock.picking views
        """,
	"category" : "Generic Modules/Stock",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["stock_view.xml", ],
	"active": False,
	"installable": False
}

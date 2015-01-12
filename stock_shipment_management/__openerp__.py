# -*- coding: utf-8 -*-
##############################################################################
#
#    Author:  Joël Grand-Guillaume
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more description.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{"name": "Shipment Management",
 "version": "0.1",
 "author": "Camptocamp",
 "category": "Transportation",
 "license": 'AGPL-3',
 'complexity': "normal",
 "images" : [],
 "website": "http://www.camptocamp.com",
 "depends" : ["delivery",
              "stock_route_transit",
              ],
 "demo": [],
 "data": ["data/shipment_plan_sequence.xml",
          "data/tranport_mode_data.xml",
          "view/shipment_plan.xml",
          "view/transport_mode.xml",
          "security/ir.model.access.csv",
          ],
 "auto_install": False,
 "test": [],
 'installable': True,
 }

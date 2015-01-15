# -*- coding: utf-8 -*-
#
#
#    Authors: Joël Grand-Guillaume, Yannick Vaucher
#    Copyright 2013-2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more description.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{"name": "Shipment Management",
 "version": "0.1",
 "author": "Camptocamp",
 "category": "Transportation",
 "license": 'AGPL-3',
 "complexity": "normal",
 "images": [],
 "website": "http://www.camptocamp.com",
 "depends": ["delivery",
             "stock_route_transit",
             "transport_information",
             ],
 "demo": [],
 "data": ["data/shipment_plan_sequence.xml",
          "wizard/shipment_carrier_setter_view.xml",
          "wizard/shipment_carrier_tracking_ref_setter_view.xml",
          "wizard/shipment_etd_setter_view.xml",
          "wizard/shipment_eta_setter_view.xml",
          "wizard/create_shipment_view.xml",
          "view/shipment_plan.xml",
          "workflow/shipment_plan.xml",
          "security/ir.model.access.csv",
          ],
 "auto_install": False,
 "test": [],
 "installable": True,
 }

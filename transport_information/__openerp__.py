# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 Camptocamp SA
#    Author: Leonardo Pistone
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

{"name": "Transport Information",
 "summary": "Transport Information",
 "version": "0.1",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "category": "Purchase Management",
 "license": "AGPL-3",
 'complexity': "easy",
 "depends": ["purchase",
             ],
 "data": ["view/transport_mode.xml",
          "view/transport_vehicle.xml",
          "security/ir.model.access.csv",
          ],
 "installable": True,
 }

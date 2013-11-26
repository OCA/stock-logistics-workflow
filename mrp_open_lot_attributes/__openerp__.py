# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

{'name': 'MRP Open Lot Attributes',
 'version': '0.1',
 'category': 'Generic Modules/Others',
 'license': 'AGPL-3',
 'description': """
This module adds buttons to edit the Production Lot information, including
custom attributes, from the Finished Products tab in the Manufacturing Order.

""",
 'complexity': 'easy',
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['mrp', 'production_lot_custom_attributes'],
 'init_xml': [],
 'update_xml': ['mrp_view.xml'],
 'demo_xml': [],
 'installable': True,
 'active': False,
 }

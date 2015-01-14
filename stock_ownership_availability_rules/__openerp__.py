# -*- coding: utf-8 -*-
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
{'name': 'Stock Ownership Availability Rules',
 'summary': 'Enforce ownership on stock availability',
 'version': '0.1',
 'author': 'Camptocamp',
 'category': 'Purchase Management',
 'license': 'AGPL-3',
 'images': [],
 'depends': ['stock',
             ],
 'demo': [],
 'data': [
     'view/quant.xml',
     'security/group.xml'
 ],
 "pre_init_hook": 'fill_quant_owner',
 'auto_install': False,
 'installable': True,
 }

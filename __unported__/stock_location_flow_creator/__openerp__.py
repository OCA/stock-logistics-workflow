# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp)
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

{'name': 'Create configuration of stock location flow',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Warehouse',
 'complexity': 'easy', #easy, normal, expert
 'depends': ['stock_location',
             'stock_orderpoint_creator'],
 'description': """
Extends orderpoint wizard to configure massively
stock location flows for multiple product""",
 'website': 'http://www.openerp.com',
 'init_xml': [],
 'update_xml': ["wizard/product_config_creator_view.xml",
                "security/ir.model.access.csv"],
 'demo_xml': [],
 'test': [],
 'installable': False,
 'images': [],
 'auto_install': True,
 'license': 'AGPL-3',
 'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

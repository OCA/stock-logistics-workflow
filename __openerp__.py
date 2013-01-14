# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with simple scenarios
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of stock_scanner
#
#    stock_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    stock_scanner is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Scanner',
    'version': '1.2',
    'category': 'Generic Modules/Inventory Control',
    'description': """Allows managing barcode readers with simple scenarios
- You can define a workfow for each object (stock picking, inventory, sale, etc)
- Works with all scanner hardware model (just SSH client required)

The "sentinel" specific ncurses client, available in the "hardware" directory, requires the "openobject-library" python module, available from pip :
    $ sudo pip install openobject-library

Some demo/tutorial scenarios are available in the "demo" directory of the module.
To import these scenarios, you can use the import script located in the "scripts" directory.
""",
    'author': 'SYLEAM',
    'website': 'http://www.Syleam.fr/',
    'depends': [
        'base',
        'product',
        'stock',
        'wms',
    ],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'stock_scanner_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'license': 'GPL-3',
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

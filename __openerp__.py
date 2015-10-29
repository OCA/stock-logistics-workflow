# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with
#    simple scenarios
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>

#    This file is a part of stock_scanner
#
#    stock_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
    'version': '1.0',
    'category': 'Generic Modules/Inventory Control',
    'author': 'SYLEAM,'
              'ACSONE SA/NV',
    'website': 'http://www.Syleam.fr/',
    'images': [],
    'depends': [
        'product',
        'stock',
    ],

    'data': [
        'security/stock_scanner_security.xml',
        'security/ir.model.access.csv',
        'data/stock_scanner_data.xml',
        'data/ir_cron.xml',
        'wizard/stock_scanner_config_wizard_view.xml',
        'stock_scanner_view.xml',
    ],

    'qweb': [],
    'demo': [
        'demo/stock_scanner_demo.xml',
        'demo/Tutorial/Tutorial.scenario',
        'demo/Tutorial/Step_types/Step_types.scenario',
        'demo/Tutorial/Sentinel/Sentinel.scenario',
        'demo/Tests/Tests.scenario',
        'demo/Tests/Barcode/Barcode.scenario',
        'demo/Stock/Stock.scenario',
        'demo/Stock/Inventory/Inventory.scenario',
        'demo/Stock/Location_informations/Location_informations.scenario',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}

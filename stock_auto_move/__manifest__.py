# -*- coding: utf-8 -*-
# Copyright 2014 NDP Systèmes (<https://www.ndp-systemes.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Automatic Move Processing',
    'version': '10.0.2.0.0',
    'author': 'NDP Systèmes, Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'depends': ['stock'],
    'data': [
        'data/stock_auto_move_data.xml',
        'views/stock_auto_move_view.xml',
        'views/stock_location_path.xml',
    ],
    'demo': [
        'demo/stock_auto_move_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}

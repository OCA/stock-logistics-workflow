# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

{
    'name': 'Automatic Move Processing',
    'version': '9.0.1.0.0',
    'author': 'NDP Systèmes, Odoo Community Association (OCA)',
    'category': 'Warehouse',
    'website': 'http://www.ndp-systemes.fr',
    'depends': ['stock'],
    'data': [
        'data/stock_auto_move_data.xml',
        'views/stock_move.xml',
        'views/procurement_rule.xml',
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

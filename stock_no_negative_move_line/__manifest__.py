# -*- coding: utf-8 -*-
{
    'name': "stock_no_negative_move_line",

    'summary': """Disallow negative stock levels by move line and validating""",

    'description': """Disallow negative stock levels by move line and validating""",

    'author': "Rooteam",
    'website': "http://www.rooteam.com",

    'category': "Inventory, Logistic, Storage",
    "version": "15.0.1.0.0",
    'license': 'AGPL-3',
    'depends': ['stock_no_negative'],

    'data': [
        'views/res_config_settings_views.xml',
    ],
}

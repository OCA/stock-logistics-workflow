# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Move Partner Reference',
    'summary': """
        Allows to add a partner reference at move level.""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'maintainers': ['rousseldenis'],
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'depends': [
        'stock',
    ],
    'data': [
        'wizards/stock_picking_fill_partner_reference.xml',
        'security/security.xml',
        'views/stock_config_settings.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
    ],
}

# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Exclude To Remove Lot',
    'summary': """
        This modules allows to exclude lots based on their removal date""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'development_status': 'Alpha',
    'maintainers': ['rousseldenis'],
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'depends': [
        'stock',
        'product_expiry',
    ],
    'data': [
        'views/stock_picking_type.xml',
    ]
}

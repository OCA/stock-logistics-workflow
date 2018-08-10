# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Pack Operation Quick Lot',
    'summary': 'Set lot name and end date directly on picking operations',
    'version': '9.0.1.0.0',
    'category': 'Stock',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'product_expiry',
    ],
    'data': [
        'views/stock_view.xml',
    ],
}

# -*- coding: utf-8 -*-
# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Reservation Condition',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'author': "Komit, Odoo Community Association (OCA)",
    'website': 'http://komit-consulting.com',
    "summary": "Avoid automatic booking of quants in some conditions",
    'depends': [
        'purchase',
        'sale',
        'stock'
    ],
    'data': [
        'views/purchase_order.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
}

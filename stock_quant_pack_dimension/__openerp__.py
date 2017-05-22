# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Quant Package Dimension',
    'summary': 'Provide dimensions on packaging',
    'version': '9.0.1.0.0',
    'category': 'Warehouse',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs', 'Odoo Community Association (OCA)'
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/stock_quant_package_view.xml',
    ],
}

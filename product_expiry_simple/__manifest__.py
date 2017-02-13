# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Expiry Simple',
    'version': '10.0.1.0.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'summary':
    'Simpler and better alternative to the official product_expiry module',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'conflicts': ['product_expiry'],
    'data': [
        'views/stock.xml',
        'data/product_removal.xml',
        ],
    'installable': True,
}

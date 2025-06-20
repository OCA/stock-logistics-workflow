# -*- coding: utf-8 -*-
{
    'name': 'Stock Product Restrict',
    'version': '16.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Restrict product creation based on user permissions',
    'description': """
Stock Product Restrict
======================

This module adds a checkbox in the user technical settings to control whether
a user can create products or only view them.

Features:
* Add 'Criar produtos' checkbox in user technical settings
* Hide 'Create' button in product views for users without permission
* Users without permission can only view products
* Creates 'Criar produtos' group in Extra Rights section for easy permission management
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'product',
        'stock',
    ],
    'data': [
        'security/stock_product_restrict.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

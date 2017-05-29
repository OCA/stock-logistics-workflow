# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Equivalences',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Quotation, Sale Orders, Delivery & Invoicing Control',
    'description': """
Simple module which adds an link on products to:
 - an equivalent product
 - a list of compatibles products (no business logic for this list)

If a product has an equivalent, it will be automatically
replaced by its equivalent in delivery orders.
""",
    'depends': ['base',
             'product',
             'packing_product_change',],
    'data': ['views/product_view.xml',],
    'installable': True,
    'auto_install': True,
}

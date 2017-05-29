# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Packing Product Change',
    'version': '10.0',
    'category': 'Hidden',
    'author': 'Camptocamp',
    'summary': 'change product in packing',
    'description': """
This module will allow you to change a product during the packing
operation. The replaced product will be shown on the generated
invoices, so the customer will be informed of the operation.

This will work only if the invoice was not generated before the
packing was made.
""",
    'website': 'http://www.camptocamp.com',
    'depends': ['sale_stock'],
    'data': [
        "wizard/replace_product_view.xml",
        "views/stock_view.xml",
        ],
    'installable': True,
    'auto_install': True,
}

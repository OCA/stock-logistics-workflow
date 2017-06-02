# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Product Equivalences',
 'version': '10.0.1.0.0',
 'license': 'AGPL-3',
 'author': "Camptocamp, "
           "Odoo Community Association (OCA)",
 'category': 'Hidden',
 'summary': 'change product in packing',
 'website': 'http://www.camptocamp.com',
 'depends': ['sale_stock'],
 'data': [
     "wizard/replace_product_view.xml",
     "views/stock_view.xml",
         ],
 'installable': True,
 'auto_install': True, }

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Product Equivalences',
 'version': '10.0.1.0.0',
 'license': 'AGPL-3',
 'author': "Camptocamp, "
           "Odoo Community Association (OCA)",
 'category': 'Hidden',
 'summary': 'Adds equivalent product link in product',
 'depends': ['base',
             'product',
             'packing_product_change', ],
 'data': ['views/product_view.xml', ],
 'installable': True,
 'auto_install': True, }

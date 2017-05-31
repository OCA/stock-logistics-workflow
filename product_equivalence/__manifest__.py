# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Product Equivalences',
 'version': '10.0.1.0.0',
 'license': 'AGPL-3',
 'author': "Camptocamp, "
           "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
           "Odoo Community Association (OCA)",
 'category': 'Hidden',
 'summary': 'Quotation, Sale Orders, Delivery & Invoicing Control',
 'depends': ['base',
                'product',
                'packing_product_change', ],
 'data': ['views/product_view.xml', ],
 'installable': True,
 'auto_install': True,
}

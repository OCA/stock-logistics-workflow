# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock batch picking',
    'version': '9.0.1.0.0',
    'author': "Camptocamp, Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Inventory',
    'complexity': "normal",
    'depends': [
        'delivery',
    ],
    'website': 'http://www.camptocamp.com/',
    'data': [
        'data/stock_batch_picking_sequence.xml',
        'views/stock_batch_picking.xml',
        'views/product_product.xml',
        'views/report_batch_picking.xml',
        'views/stock_picking.xml',
        'views/stock_warehouse.xml',
        'wizard/batch_picking_creator_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False
}

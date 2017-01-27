# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Delivery Rates',
    'summary': 'Extends notion of delivery carrier rate quotes to sale orders',
    'version': '9.0.1.0.0',
    'category': 'Delivery, Stock, Sales',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock_picking_rate',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/product_template.xml',
        'demo/product_product.xml',
        'demo/delivery_carrier.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/stock_picking.xml',
        'demo/stock_picking_rate.xml',
        'demo/delivery_carrier_rate.xml',
    ],
}

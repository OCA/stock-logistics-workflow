# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Automatic Move Processing For Sale Delivery',
    'version': '8.0.1.0.0',
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Warehouse',
    'depends': [
        'sale_stock',
        'stock_auto_move'
    ],
    'data': [
        'data/sale_workflow.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    'application': False,
}

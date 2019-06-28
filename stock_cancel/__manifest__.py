# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Cancel',
    'version': '10.0.0.1.1',
    'category': 'Stock',
    'summary': "This module allows you to bring back a completed stock "
               "picking to draft state",
    'author': "www.andreacometa.it,Odoo Community Association (OCA)",
    'website': 'http://www.andreacometa.it',
    'license': 'AGPL-3',
    'depends': ['stock_picking_invoice_link'],
    'data': [
        'view/stock_view.xml',
        ],
    'installable': True,
    'images': ['images/stock_picking.jpg'],
}

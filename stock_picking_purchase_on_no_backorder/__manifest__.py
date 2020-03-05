# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Purchase On No Backorder',
    'version': '10.0.1.0.0',
    'author': "PlanetaTIC,Odoo Community Association (OCA)",
    'category': 'Stock',
    'depends': [
        'sale_purchase_rel',
    ],
    'description': """Stock Picking Purchase On No Backorder""",
    'website': 'https://github.com/OCA/margin-analysis',
    'data': [
        'views/partner_view.xml',
    ],
    'test': [],
    'license': 'AGPL-3',
    'installable': True,
}

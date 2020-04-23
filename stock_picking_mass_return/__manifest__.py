# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Mass Return',
    'version': '10.0.1.0.0',
    'description': 'New wizard to return products to their supplier',
    'author': "PlanetaTIC, Odoo Community Association (OCA)",
    'category': 'Stock',
    'depends': [
        'stock',
    ],
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'data': [
        'wizard/mass_return_view.xml',
    ],
    'test': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
# © 2016 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Procurement Select Route',
    'version': '9.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'summary': (
        'Manually select the route of a product on a '
        'procurement exception.'
    ),
    'depends': ['purchase', 'sale_mrp'],
    'data': [
        'views/procurement_order.xml',
    ],
    'installable': True,
    'application': False,
}

# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Stock Truck Unloading Time',
    'version': '14.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Stock',
    'depends': [
        # core
        'stock',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
}

# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Show Date Done',
    'summary': 'Show and group date_done of Stock Pickings',
    'version': '10.0.1.0.0',
    'category': 'Warehouse Management',
    'author': 'PlanetaTIC, Odoo Community Association (OCA)',
    'website': 'https://www.planetatic.com',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_picking_view.xml',
    ],
}

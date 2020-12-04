# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Stock Picking Unreserve Line',
    'summary': 'Permits to unreserve lines of stock picking',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'PlanetaTIC'
              ' Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_move_views.xml',
    ],
    'installable': True,
    'auto_install': False
}

# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Auto Create Lot',
    'summary': 'Auto create lots for incoming pickings',
    'version': '12.0.1.0.0',
    'development_status': 'Production/Stable',
    'category': 'stock',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'stock',
    ],
    'data': [
        'views/product_views.xml',
        'views/stock_picking_type_views.xml',
    ],
    'maintainers': ['sergio-teruel'],
}

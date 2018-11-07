# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Whole Scrap',
    'summary': 'Create whole scrap from a picking for move lines',
    'version': '11.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Warehouse',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'stock',
    ],
    'data': [
        'wizards/stock_picking_whole_scrap.xml',
        'views/stock_picking_views.xml',
    ],
}

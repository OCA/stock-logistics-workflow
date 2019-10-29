# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale margin sync',
    'summary': 'Recompute sale margin when stock move cost price is changed',
    'version': '11.0.1.0.0',
    'category': 'Stock',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'sale_margin',
        'sale_stock',
    ],
    'data': [
    ],
}

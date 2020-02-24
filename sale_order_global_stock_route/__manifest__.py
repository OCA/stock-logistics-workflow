# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Global Stock Route',
    'summary': 'Add the possibility to choose '
               'one warehouse path for an order',
    'version': '12.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Warehouse',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
}

#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Line Kit Component Route',
    'summary': 'When selling a Kit, procure the Components instead of the Kit.',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'website': 'https://github.com/OCA/stock-logistics-workflow'
               '/tree/12.0/sale_order_line_kit_component_rule',
    'author': 'TAKOBI, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'mrp',
        'sale_stock',
    ],
}

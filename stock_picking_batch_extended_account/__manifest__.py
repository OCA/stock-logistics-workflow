# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Stock batch picking account',
    'summary': 'Generates invoices when batch is set to Done state',
    'version': '12.0.1.0.0',
    'author': "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["ernestotejeda"],
    'development_status': 'Beta',
    'category': 'Warehouse Management',
    'depends': [
        'stock_picking_batch_extended',
    ],
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'data': [
        'views/stock_batch_picking.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}

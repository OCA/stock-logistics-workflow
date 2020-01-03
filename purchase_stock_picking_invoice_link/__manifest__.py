# Copyright 2019 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Purchase Stock Picking Invoice Link',
    'version': '11.0.1.0.0',
    'category': 'Warehouse Management',
    'summary': 'Adds link between purchases, pickings and invoices',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'http://github.com/OCA/stock-logistics-workflow',
    'license': 'AGPL-3',
    'depends': [
        'stock_picking_invoice_link',
        'purchase',
    ],
    'data': [
        'views/account_invoice_views.xml',
    ],
    'installable': True,
}

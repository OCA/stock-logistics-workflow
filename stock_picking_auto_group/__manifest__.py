# Copyright 2020 Ryan Cole (www.ryanc.me)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


{
    'name': 'Auto-Group Stock Pickings',
    'summary': 'Automatically create procurement groups for individual stock pickings.',
    'author': 'Ryan Cole, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Inventory',
    'depends': [
        'stock',
    ],

    'data': [
        'views/views.xml',
    ],

    'installable': True,
    'application': False,
}

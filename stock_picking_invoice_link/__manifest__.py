# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2016 AvanzOSC (<http://www.avanzosc.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock Picking Invoice Link',
    'version': '8.0.1.1.0',
    'category': 'Warehouse Management',
    'summary': 'Adds link between pickings and generated invoices',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': ['stock_account'],
    'data': [
        'views/stock_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}

# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2016 AvanzOSC (<http://www.avanzosc.es>)
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock Picking Invoice Link',
    'version': '9.0.2.0.0',
    'category': 'Warehouse Management',
    'summary': 'Adds link between pickings and invoices',
    'author': 'Agile Business Group, '
              'Tecnativa, '
              'BCIM sprl, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': ['sale_stock'],
    'data': [
        'views/stock_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}

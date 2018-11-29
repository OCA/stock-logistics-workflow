# Copyright 2013-17 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2016 AvanzOSC (<http://www.avanzosc.es>)
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock Picking Invoice Link',
    'version': '11.0.1.0.1',
    'category': 'Warehouse Management',
    'summary': 'Adds link between pickings and invoices',
    'author': 'Agile Business Group, '
              'Tecnativa, '
              'BCIM sprl, '
              'Softdil S.L, '
              'Odoo Community Association (OCA)',
    'website': 'http://github.com/OCA/stock-logistics-workflow',
    'license': 'AGPL-3',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/stock_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}

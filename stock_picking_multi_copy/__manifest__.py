# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Multi Copy',
    'summary': 'Permits to print multiple copies of a stock picking',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'PlanetaTIC'
              ' Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-warehouse',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'report/report_deliveryslip.xml',
        'views/res_partner_view.xml',
        'views/stock_warehouse_view.xml',
    ],
    'installable': True,
    'auto_install': False
}

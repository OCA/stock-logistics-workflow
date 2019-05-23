# Copyright 2019 Komit Consulting - Duc Dao Dong
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': 'Stock Landed Costs Currency',
    'version': '12.0.1.0.0',
    "author": "Komit Consulting,"
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Stock Accounting',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'depends': [
        'stock_landed_costs',
    ],
    'data': [
        'views/stock_landed_cost_views.xml',
    ],

    'installable': True,
}

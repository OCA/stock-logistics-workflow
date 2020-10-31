# Copyright 2016-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Xtendoo Last Price Costing Method',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': "Add a new Costing Method 'Last Price'",
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'depends': ['stock',
                'stock_account',
                'purchase'
                ],
    'data': ['views/product.xml'],
    'installable': True,
}

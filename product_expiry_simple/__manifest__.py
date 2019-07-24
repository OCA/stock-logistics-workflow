# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2018 Jarsa Sistemas (Alan Ramos <alan.ramos@jarsa.com.mx>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Expiry Simple',
    'version': '11.0.1.1.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'summary':
    'Simpler and better alternative to the official product_expiry module',
    'author': 'Akretion,Jarsa Sistemas,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': [
        'stock',
    ],
    'conflicts': [
        'product_expiry'
    ],
    'data': [
        'views/stock.xml',
        'data/product_removal.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
}

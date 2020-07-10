# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Sale Order',
    'version': '12.0.1.0.0',
    'author': 'Odoo Nodriza Tech (ONT),Odoo Community Association (OCA)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'sale', 'stock'],
    'data': [
        'views/stock_picking.xml'
    ],
    'installable': True,
    'auto_install': False,
}
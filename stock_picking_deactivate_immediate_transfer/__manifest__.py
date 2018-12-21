# Copyright 2015-18 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Picking Deactivate Immediate Transfer',
    'version': '11.0.1.0.0',
    'category': 'Warehouse Management',
    'summary': "Deactivates immediate transfers"
               "sticking only to planned ones",
    'author': "Eficent, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'license': "AGPL-3",
}

# Copyright 2015-18 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Picking Deactivate Immediate Transfer',
    'summary': "Deactivates immediate transfers"
               "sticking only to planned ones",
    'version': '11.0.1.0.0',
    'category': 'Warehouse Management',
    'author': "Eficent, "
              "Odoo Community Association (OCA)",
    'website': "http://www.github.com/OCA/stock-logistics-workflow",
    'license': "AGPL-3",
    'depends': [
        'stock'
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}

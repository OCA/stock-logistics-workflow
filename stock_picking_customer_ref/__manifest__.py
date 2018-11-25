# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2015 AvanzOSC - Ana Juaristi
# Copyright 2015 AvanzOSC - Mikel Arregi
# Copyright 2015 AvanzOSC - Alfredo de la Fuente
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Stock Picking Customer Reference',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'author': 'AvanzOSC,'
              'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'license': 'AGPL-3',
    'summary': 'This module displays the sale reference/description in the '
               'pickings',
    'depends': [
        'sale_stock'
    ],
    'data': [
        'views/stock_picking_view.xml'
    ],
    'installable': True,
}

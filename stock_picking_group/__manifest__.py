# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Group',
    'summary': 'Permits to group pickings by partner and carrier',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'PlanetaTIC'
              ' Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/report_grouped_deliveryslip.xml',
        'report/picking_group_report_views.xml',
        'views/stock_picking_group_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

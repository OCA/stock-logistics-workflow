# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Unassign Wizard',
    "summary": "Permits to unassign reserved stock from other stock.move",
    'version': '12.0.1.0.1',
    "development_status": "Production/Stable",
    "category": "Stock",
    'author': "PlanetaTIC,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'depends': [
        'stock',
        'stock_picking_unreserve_line',
        'mrp',
    ],
    'demo': [],
    'data': [
        'views/stock_picking_view.xml',
        'views/mrp_production_view.xml',
        'wizard/stock_unassign_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# Copyright 2021 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Purchase Limit Days',
    "summary": "Do not purchase products required for orders beyond X days",
    'version': '12.0.1.0.1',
    "development_status": "Production/Stable",
    'category': 'Stock',
    'author': "PlanetaTIC,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/edi',
    'depends': [
        'stock',
    ],
    'demo': [],
    'data': [
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'auto_install': False,
}

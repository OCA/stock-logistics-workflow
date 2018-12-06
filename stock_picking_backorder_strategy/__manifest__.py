# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Picking backordering strategies',
    'version': '11.0.1.0.0',
    'development_status': 'Production/Stable',
    'author': """ACSONE SA/NV,
                 Odoo Community Association (OCA)""",
    'maintainers': [
        'rousseldenis',
        'mgosai'
    ],
    'category': 'Warehouse Management',
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'depends': [
        'stock',
    ],
    'data': [
        'views/picking_type.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}

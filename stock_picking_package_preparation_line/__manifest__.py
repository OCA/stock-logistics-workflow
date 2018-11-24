# -*- coding: utf-8 -*-
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
#    Copyright 2015-2018 Lorenzo Battistini - Agile Business Group
#    Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Picking Package Preparation Line',
    'version': '10.0.1.0.3',
    'author': 'Apulia Software srl, Odoo Italia Network,'
    'Odoo Community Association (OCA)',
    'maintainer': 'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Warehouse Management',
    'depends': [
        'stock',
        'product',
        'stock_picking_package_preparation',
    ],
    'website': 'http://www.apuliasoftware.it',
    'data': [
        'views/ir_config_view.xml',
        'views/stock_picking_package_preparation_line.xml',
        'security/ir.model.access.csv',
        'security/package_preparation_line_security.xml',
    ],
    'installable': True,
    'auto_install': False,
}

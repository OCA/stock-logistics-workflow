# -*- coding: utf-8 -*-
# Author: Guewen Baconnier
# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Picking Package Preparation',
    'version': '10.0.1.0.1',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'maintainer': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Warehouse Management',
    'depends': ['stock'],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/stock_picking_package_preparation_view.xml',
        'security/ir.model.access.csv',
        'security/package_preparation_security.xml'],
    'installable': True,
    'auto_install': False,
}

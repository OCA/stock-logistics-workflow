# -*- coding: utf-8 -*-
# © 2015 Leonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Stock Ownership By Move',
 'summary': 'Preserve Ownership of moves (not pickings) on reception.',
 'version': '10.0.0.1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Warehouse Management',
 'license': 'AGPL-3',
 'images': [],
 'depends': ['stock'],
 'data': [
     'security/group.xml',
     'view/move.xml',
     'view/picking.xml',
 ],
 'auto_install': False,
 'installable': True,
 }

# -*- coding: utf-8 -*-
# Copyright 2014 ALeonardo Pistone, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Stock Ownership Availability Rules',
 'summary': 'Enforce ownership on stock availability',
 'version': '10.0.1.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Purchase Management',
 'license': 'AGPL-3',
 'images': [],
 'depends': ['stock',
             ],
 'demo': [],
 'data': [
     'view/quant.xml',
     'view/move.xml',
     'security/group.xml'
 ],
 "pre_init_hook": 'fill_quant_owner',
 'auto_install': False,
 'installable': True,
 }

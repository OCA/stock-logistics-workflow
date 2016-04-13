# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Picking dispatch',
 'version': '8.0.1.2.3',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'complexity': "normal",  # easy, normal, expert
 'depends': ['stock',
             'delivery',
             ],
 'website': 'http://www.camptocamp.com/',
 'data': [
     'data/cron.xml',
     'data/picking_dispatch_sequence.xml',
     'views/picking_dispatch.xml',
     'views/product_product.xml',
     'views/report_picking_dispatch.xml',
     'views/stock_picking.xml',
     'views/stock_move.xml',
     'wizard/create_dispatch_view.xml',
     'wizard/dispatch_assign_picker_view.xml',
     'wizard/dispatch_start_view.xml',
     'wizard/check_assign_all_view.xml',
     'security/ir.model.access.csv',
     'security/security.xml',
 ],
 'tests': [],
 'installable': False,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False
 }

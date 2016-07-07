# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Delivery Orders Mass Assign',
    'version': '9.0.1.0.0',
    'author': "Camptocamp,GRAP,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Warehouse Management',
    'depends': ['stock'],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/cron_data.xml',
        'wizard/check_assign_all_view.xml',
    ],
    "test": [
        'test/test_check_assign_all.yml',
    ],
    'installable': True,
    'auto_install': False,
}

# © 2014-2016 Camptocamp SA (Guewen Baconnier)
# © 2017 JARSA Sistemas S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Delivery Orders Mass Assign',
    'version': '11.0.1.0.0',
    'author': ("Camptocamp,GRAP,Odoo Community Association (OCA),"
               "JARSA Sistemas S.A. de C.V."),
    'license': 'AGPL-3',
    'category': 'Warehouse Management',
    'description': 'Module to assign multiple orders',
    'depends': ['stock'],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/cron_data.xml',
        'wizard/check_assign_all_view.xml',
    ],
    'installable': True,
}

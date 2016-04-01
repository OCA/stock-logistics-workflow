# -*- coding: utf-8 -*-
# © 2016 Agile Business Group (<http://www.agilebg.com>)
# © 2015 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Stock Move Backdating',
    'version': '8.0.1.0.0',
    'category': 'Stock Logistics',
    'author': 'Marco Dieckhoff, BREMSKERL, Agile Business Group,'
    ' Odoo Community Association (OCA)',
    'website': 'www.bremskerl.com',
    'depends': ['stock_account'],
    'data': [
        'wizards/stock_transfer_details_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

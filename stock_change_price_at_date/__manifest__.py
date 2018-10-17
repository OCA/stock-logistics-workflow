# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Change Price At Date',
    'summary': """
        This module allows to fill in a date in the standard wizard that
        changes product price. That helps accountant to add some product
        past values""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'stock_account',
    ],
    'data': [
        'wizards/stock_change_standard_price.xml',
    ],
}

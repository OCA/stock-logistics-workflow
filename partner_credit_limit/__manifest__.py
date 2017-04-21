# -*- coding: utf-8 -*-
# Copyright 2017 Ursa Information Systems <http://www.ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Credit Limit",
    "summary": "Do not ship if customer is over credit limit",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ursa Information Systems, Odoo Community Association (OCA)",
    "category": "Logistics",
    "website": "http://www.ursainfosystems.com",
    "depends": [
        "account",
        "sale_stock",
    ],
    "data": [
        "security/partner_credit_limit.xml",
        "views/res_partner.xml",
        "views/sale.xml",
        "views/stock.xml",
    ],
    "installable": True,
}

# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock no extra move",
    "summary": "Prevent creation of extra moves in picking processing",
    "version": "8.0.1.0.0",
    "category": "Logistics",
    "website": "https://camptocamp.com/",
    "author": "Odoo Community Association (OCA),Camptocamp SA",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'stock',
    ],
    "data": [
        'security/groups.xml',
        'views/stock_config_settings.xml',
        'views/stock_picking_type.xml',
    ],
}

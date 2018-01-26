# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Items Lend",
    "version": "10.0.0.1.0",
    "category": "Stock",
    "author": "JARSA Sistemas S.A. de C.V.,Odoo Community Association (OCA)",
    "website": "https://www.jarsa.com.mx/",
    "depends": [
        "stock"
    ],
    "summary": "Management Of Items Lend",
    "license": "AGPL-3",
    "data": [
        'data/ir_sequence_data.xml',
        'data/stock_location_data.xml',
        'data/stock_picking_type_data.xml',
        'data/stock_location_route_data.xml',
    ],
    "installable": True,
}

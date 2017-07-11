# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Delivery Internal",
    "summary": "Adds an internal carrier to delivery options",
    "version": "10.0.1.0.0",
    "category": "Inventory, Logistics, Warehousing",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "delivery",
    ],
    "data": [
        "data/stock_pickup_request.xml",
        "views/delivery_carrier_view.xml",
        "views/stock_pickup_request_view.xml",
        "security/ir.model.access.csv",
    ],
}

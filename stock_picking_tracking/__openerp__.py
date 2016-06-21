# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Tracking",
    "summary": "Adds a concept of event tracking for stock pickings",
    "version": "9.0.1.0.0",
    "category": "Inventory, Logistics, Warehousing",
    "website": "https://laslabs.com/",
    "author": "LasLabs",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
        "views/stock_picking_tracking_group_view.xml",
        'views/stock_picking_tracking_event_view.xml',
        'views/stock_picking_tracking_location_view.xml',
    ],
    'demo': [
        'demo/stock_tracking_demo.xml',
    ]
}

# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Picking Tracking",
    "summary": "Adds a concept of event tracking for stock pickings",
    "version": "9.0.1.0.0",
    "category": "Inventory, Logistics, Warehousing",
    "website": "https://laslabs.com/",
    "author": "LasLabs",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
        "views/stock_picking_tracking_group_view.xml",
        "views/stock_picking_tracking_event_view.xml",
        "views/stock_picking_tracking_location_view.xml",
        "views/stock_menu.xml",
    ],
    "demo": [
        "demo/stock_tracking_demo.xml",
    ]
}

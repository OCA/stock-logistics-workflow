# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Rate",
    "summary": "Adds a concept of rate quotes for stock pickings",
    "version": "9.0.1.0.0",
    "category": "Inventory, Logistics, Warehousing",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "delivery",
        'purchase',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
        "views/stock_picking_dispatch_rate_view.xml",
        'wizards/stock_picking_dispatch_rate_purchase_view.xml',
    ],
}

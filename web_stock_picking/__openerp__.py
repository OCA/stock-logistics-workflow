# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Web Stock Picking",
    "summary": "Add web/barcode workflows for stock picking.",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://laslabs.com/",
    "author": "LasLabs",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        'barcodes',
        "stock",
        "website_form",
    ],
    "data": [
        'wizards/web_stock_picking_wizard_template.xml',
        'views/assets.xml',
        'views/web_warehouse.xml',
        'views/stock_warehouse.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [
        'demo/web_stock_picking_demo.xml',
    ],
}

# Copyright 2022 Camptocamp SA, Trobz
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Improved Stock Product Label",
    "summary": "Make customizing printing product label more flexible",
    "version": "15.0.1.0.0",
    "author": "Trobz, Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Inventory",
    "depends": ["base_selection", "product", "stock"],
    "installable": True,
    "data": [
        "data/product_label_formats.xml",
        "wizard/product_label_layout_views.xml",
    ],
}

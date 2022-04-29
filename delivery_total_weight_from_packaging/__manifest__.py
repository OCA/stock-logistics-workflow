# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
{
    "name": "Delivery Total Weight From Packaging",
    "summary": "Include packaging weight on move, transfer and package.",
    "version": "13.0.1.1.2",
    "development_status": "Alpha",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        # core
        "delivery",
        # OCA/product-attribute
        "product_total_weight_from_packaging",
    ],
    "data": [],
}

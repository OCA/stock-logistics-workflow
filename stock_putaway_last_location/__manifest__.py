# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Putaway Last Location",
    "summary": "Use the last putaway location of a product as the default"
    "putaway location for this product.",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["paradoxxxzero"],
    "depends": ["stock"],
    "data": [
        "views/stock_location_views.xml",
    ],
}

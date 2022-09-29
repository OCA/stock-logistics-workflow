# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock lot product qty search",
    "summary": "Allows to search on Quantity field of Lot/Serial Numbers",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_production_lot.xml",
    ],
}

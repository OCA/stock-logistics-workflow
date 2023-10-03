# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Lot Show Quantity and Location",
    "summary": "Adds computed fields to show, for each serial/lot, "
    "the quantityand the location",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Ooops404, PyTech SRL, Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["pytech-bot,", "aleuffre"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_production_lot.xml",
    ],
}

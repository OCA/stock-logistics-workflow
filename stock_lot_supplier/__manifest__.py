# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Lot Supplier",
    "summary": "Track the supplier on lot/serial numbers set during receipt",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["account", "stock"],
    "data": [
        "views/stock_lot_views.xml",
    ],
    "installable": True,
    "application": False,
}

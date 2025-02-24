# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
{
    "name": "Stock Rule Location Picking Type",
    "summary": "Allows to create stock.moves from procurements and take the destination"
    " location of the resulting moves to be the one defined in the picking type.",
    "version": "17.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": ["views/stock_rule_view.xml"],
}

# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Line Split",
    "summary": "Split stock move lines into smaller move lines.",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Inventory/Inventory",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_move_line_split_views.xml",
        "views/stock_move_line_views.xml",
    ],
}

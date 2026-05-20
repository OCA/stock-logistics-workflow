# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Stock Delivery Qty Picked",
    "summary": "Use qty_picked for shipping weight when putting in pack",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock_delivery",
        "stock_move_line_qty_picked",
    ],
    "data": [],
    "installable": True,
}

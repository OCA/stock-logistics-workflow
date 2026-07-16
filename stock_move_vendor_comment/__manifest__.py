# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Vendor Comment",
    "summary": """Add the vendor comment field to stock move""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_move_line_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}

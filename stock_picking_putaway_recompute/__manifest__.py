# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Putaway Recompute",
    "summary": """
        This module allows to recompute the picking operations putaways if
        configurations have changed""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["rousseldenis"],
    "depends": ["stock"],
    "data": [
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
        "views/stock_move_line.xml",
    ],
}

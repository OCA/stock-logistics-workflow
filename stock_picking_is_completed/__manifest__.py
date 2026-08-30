# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Is Completed",
    "summary": """
        This module adds a field on stock picking that will check if all movements
        have been filled in by stock operator""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
}

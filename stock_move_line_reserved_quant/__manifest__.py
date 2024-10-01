# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Line Reserved Quant",
    "summary": """
        This module allows to get the link from a stock move line
        to the reserved quant""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["rousseldenis"],
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_move_line.xml",
    ],
}

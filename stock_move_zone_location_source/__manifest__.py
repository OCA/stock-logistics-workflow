# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Zone Location Source",
    "summary": """
        Allows to retrieve for a given stock move, the origin location zone (e.g. 'Stock')""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["rousseldenis"],
    "depends": [
        "stock",
        "stock_location_zone",
    ],
    "data": [
        "views/stock_location.xml",
        "views/stock_move.xml",
        "views/stock_picking.xml",
    ],
}

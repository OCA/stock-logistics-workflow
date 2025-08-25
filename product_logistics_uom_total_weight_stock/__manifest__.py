# Copyright 2025 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product Logistics UoM Total Weight Stock",
    "summary": """
        Adds total weight computation on stock moves and pickings
        based on product weight and UoM.
    """,
    "version": "17.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Antoni Marroig, APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock", "product_logistics_uom"],
    "data": [
        "views/stock_quant_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_move.xml",
    ],
}

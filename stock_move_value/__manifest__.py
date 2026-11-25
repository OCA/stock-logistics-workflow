# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Move Value",
    "summary": "Add value fields to stock moves for valuation visibility",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "stock",
    "license": "AGPL-3",
    "depends": ["stock_account"],
    "data": [
        "views/stock_move_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}

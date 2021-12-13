# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Enforce manually selected lot",
    "summary": "Force the user to manually select a lot",
    "version": "12.0.1.1.0",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": (
        "Hunki Enterprises BV,"
        "Opener B.V.,"
        "Odoo Community Association (OCA)"
    ),
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
        "base_view_inheritance_extension",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_move_line.xml",
        "views/stock_picking_type.xml",
    ],
    "post_init_hook": "post_init_hook",
}

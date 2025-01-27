# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Move: group by release blocked",
    "Summary": "Group stock moves in 1 picking based on release blocked",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse",
    "depends": [
        "stock_picking_group_by_base",
        "stock_available_to_promise_release_block",
    ],
    "data": ["views/stock_picking_type.xml"],
    "installable": True,
    "license": "AGPL-3",
    "auto_install": True,
}

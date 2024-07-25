# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Operation Manual Lot Selection",
    "Summary": "Force the user to manually select a production lot",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock", "product"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}

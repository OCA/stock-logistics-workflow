# Copyright (C) 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move - Disable Extra for Lot Preservation",
    "summary": "Add option to disable extra moves to preserve lot information "
    "on excess quantity",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_move_views.xml",
    ],
    "installable": True,
}

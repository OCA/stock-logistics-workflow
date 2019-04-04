# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Stock Picking Restrict Cancel",
    "summary": "Restrict cancellation with Purchase.",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "purchase",
        "stock_picking_restrict_cancel_with_orig_move",
    ],
    'auto_install': True,
}

# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Reservation Policy",
    "summary": "Reserve a transfer's moves all-or-nothing instead of partially.",
    "version": "19.0.1.0.0",
    "category": "Inventory/Configuration",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "maintainers": ["ivantodorovich"],
    "depends": ["stock"],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
    ],
}

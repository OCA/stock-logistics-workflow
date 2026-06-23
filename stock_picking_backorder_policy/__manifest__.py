# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Backorder Policy",
    "summary": "Override the operation type backorder policy per partner or transfer.",
    "version": "19.0.1.0.0",
    "category": "Inventory/Configuration",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "maintainers": ["ivantodorovich"],
    "depends": ["stock"],
    "data": [
        "views/res_partner_views.xml",
        "views/stock_picking_views.xml",
    ],
}

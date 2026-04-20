# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Batch Partner Enable",
    "summary": "Control the Automatic Batches grouping per partner",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": ["stock_picking_batch"],
    "data": [
        "views/res_partner.xml",
    ],
}

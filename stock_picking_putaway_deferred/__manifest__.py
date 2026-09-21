# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Putaway Deferred",
    "summary": "Defer putaway calculation from reservation to operator time",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["lmignon"],
    "depends": ["stock_picking_putaway_recompute"],
    "data": [
        "views/stock_picking_type.xml",
        "views/stock_picking.xml",
    ],
}

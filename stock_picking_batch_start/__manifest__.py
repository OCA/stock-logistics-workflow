# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Batch start",
    "summary": """
        This module depends on the `stock_picking_start` module, which allows for users
        to start of all individual pickings through buttons accessible on the batch
        form view.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_picking_batch", "stock_picking_start"],
    "data": ["views/stock_picking_batch.xml"],
    "demo": [],
    "installable": True,
}

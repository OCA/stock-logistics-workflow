# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Batch Actual Date",
    "summary": "Propagate a batch actual date to its pickings",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Stock",
    "license": "AGPL-3",
    "depends": [
        "stock_picking_batch",
        "stock_move_actual_date",
    ],
    "data": [
        "views/stock_picking_batch_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}

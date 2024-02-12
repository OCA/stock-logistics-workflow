# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Picking To Batch Group Field",
    "summary": "Allows to create batches grouped by picking fields.",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_picking_batch",
    ],
    "excludes": [
        "stock_picking_batch_extended",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/stock_picking_to_batch_views.xml",
    ],
}

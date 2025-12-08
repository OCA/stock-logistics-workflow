# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Picking Batch Planner",
    "summary": "Allow planning origin batches/waves from destination batch/wave",
    "version": "18.0.1.0.1",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual", "Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_picking_batch",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_batch_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "uninstall_hook": "uninstall_hook",
}

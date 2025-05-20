# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Picking Batch Print Pickings",
    "summary": "Print Picking from Stock Picking Batch",
    "version": "17.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_picking_batch",
    ],
    "data": [
        "views/stock_picking_type_views.xml",
        "views/stock_picking_batch_views.xml",
        "views/report_picking_batch_print_pickings.xml",
        "report/stock_picking_batch_print_pickings_report.xml",
    ],
}

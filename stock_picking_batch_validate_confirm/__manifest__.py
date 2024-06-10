# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Picking Batch Validate Confirm",
    "summary": "Request confirmation when validating batch if there are pending origin moves",
    "version": "16.0.1.1.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "stock_picking_batch",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_picking_batch_validate_confirm_groups.xml",
        "wizards/stock_picking_batch_confirm.xml",
    ],
}

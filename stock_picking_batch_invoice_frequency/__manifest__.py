# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Stock Picking Batch Invoice Frequency",
    "summary": "Invoice Sale Orders from Stock Pickin Batch",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual", "rafaelbn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_picking_batch",
        "sale_invoice_frequency",
    ],
    "data": [
        "views/sale_invoice_frequency.xml",
    ],
}

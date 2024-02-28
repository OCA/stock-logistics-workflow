# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Stock Picking Invoice Frequency",
    "summary": "Invoice Sales when Picking is done",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "EmilioPascual", "rafaelbn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "sale_invoice_frequency",
    ],
    "data": [
        "views/sale_invoice_frequency.xml",
    ],
}

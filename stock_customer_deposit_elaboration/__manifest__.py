# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Customer Deposit Elaboration",
    "summary": "Glue module betwen stock_customer_deposit and sale_elaboration",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual", "rafaelbn"],
    "license": "AGPL-3",
    "application": False,
    "auto_install": True,
    "depends": [
        "stock_customer_deposit",
        "sale_elaboration",
    ],
}

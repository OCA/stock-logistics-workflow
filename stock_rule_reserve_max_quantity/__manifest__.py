# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Rule Reserve Max Quantity",
    "summary": "Allows to reserve max available quantity when a move comes from an stock rule",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_rule_views.xml",
    ],
}

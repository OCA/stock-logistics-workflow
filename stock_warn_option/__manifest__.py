# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Warn Option",
    "summary": "Add Options to Stock Warn Messages",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["stock", "base_warn_option"],
    "data": [
        "views/res_partner_views.xml",
    ],
}

# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Reporting Access",
    "summary": "Add a security group for inventory reporting access",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "license": "AGPL-3",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "security/security.xml",
        "views/stock_menu_views.xml",
    ],
    "installable": True,
}

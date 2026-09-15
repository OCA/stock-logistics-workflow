# Copyright 2026
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Portal Owner",
    "summary": "Show consignment owner stock operations in portal",
    "version": "17.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["stock", "portal", "stock_picking_portal"],
    "data": [
        "security/stock_picking_portal_owner_rule.xml",
        "views/stock_picking_portal_owner_templates.xml",
    ],
    "installable": True,
}

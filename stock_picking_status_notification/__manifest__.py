# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Notify Users about Picking",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Notify selected internal users of changes in picking states",
    "depends": ["stock", "web_notify"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_notification_template_view.xml",
        "views/menuitems.xml",
    ],
    "demo": [
        "demo/stock_picking_notification_template_demo.xml",
    ],
    "license": "AGPL-3",
}

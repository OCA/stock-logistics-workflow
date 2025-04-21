# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Portal",
    "summary": "Show customer delivery orders in portal",
    "version": "16.0.1.0.0",
    "depends": ["sale_stock"],
    "author": "Cetmix OÜ, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "security/ir.model.access.csv",
        "security/stock_picking_portal_rule.xml",
        "views/res_config_settings_view.xml",
        "views/stock_picking_template.xml",
        "wizards/picking_link_wizard.xml",
    ],
    "demo": ["data/demo.xml"],
    "installable": True,
}

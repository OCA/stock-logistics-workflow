# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Fast Package Move Between Locations",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Move packages between locations directly from the 'Package' menu",
    "depends": ["stock_picking_move_package_to_package"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "wizard/stock_quant_package_fast_move_wizard.xml",
        "views/res_config_settings_view.xml",
    ],
    "license": "AGPL-3",
}

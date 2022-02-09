# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Auto Unreserve",
    "summary": "Unreserve waiting and ready pickings to reserve current picking",
    "version": "12.0.1.1.0",
    "development_status": "Beta",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "security/stock_picking_force_assign_security.xml",
        "data/ir_config_parameter.xml",
        "views/stock_picking.xml",
    ],
    "demo": [
        "demo/res_groups.xml",
    ],
}

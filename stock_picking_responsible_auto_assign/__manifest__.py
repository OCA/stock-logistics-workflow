# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Responsible Auto Assign",
    "summary": "Assign the picking responsible automatically balancing the workload",
    "version": "19.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "maintainers": ["alan196"],
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "data/ir_actions_server.xml",
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
}

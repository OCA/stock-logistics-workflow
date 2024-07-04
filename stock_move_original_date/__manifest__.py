# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Move Original Scheduled Date",
    "summary": "adds the Original Date Scheduled to stock moves.",
    "version": "15.0.1.0.0",
    "category": "Warehouse Management",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["stock"],
    "data": ["views/stock_move_views.xml", "views/stock_picking_views.xml"],
}

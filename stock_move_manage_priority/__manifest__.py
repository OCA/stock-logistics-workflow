# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Move Priority Management",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "stock",
    "depends": ["stock"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "security/groups.xml",
        "views/res_config_settings_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}

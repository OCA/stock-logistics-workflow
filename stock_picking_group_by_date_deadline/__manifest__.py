# Copyright 2023 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking: Group by deadline date",
    "summary": "This avoid to mixed stock moves with different deadlines",
    "version": "14.0.1.0.0",
    "author": "Pierre Verkest <pierreverkest84@gmail.com>, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["petrus-v"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
